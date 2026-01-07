/*
 * GreenHouseLogger.cpp
 *
 *  Created on: Aug 26, 2020
 *      Author: ojesc
 */

#include <Devices/GreenHouseLogger/GreenHouseLogger.h>
#include <Infrastructures/Json/Json.h>
#include <Infrastructures/Calendar/S@Calendar.h>
#include <math.h>

namespace SAKE {
namespace Products {
namespace iSmart {

using namespace SAKE::Library::Infrastructures;

#define ReadLog(i, to) log.Read(i*sizeof(LOG), (uint8_t*)&to, sizeof(to))
#define IsUsed(log) log.time != 0xFFFFFF

GreenHouseLogger::GreenHouseLogger(AppConfig& _appConfig,
		IApplicationConfig& _config,
		IRTOSController& _rtos,
		ITimer& _timer,
		WebRequest& _web,
		ICommChannel& _remoteSocket,
		ICommChannel& _localSocket,
		ICommChannel& _localBroadcastChannel,
		ICrypt& _crypt,
		IOTAClient& _otaClient,
		IPinOutput& _indicator,
		IStorage& _nvRam,
		IStorage& _log,
		II2C& _i2c,
		IPinOutput& _control)
:LoggingSmartDeviceBase<GreenState, GreenLog>(_appConfig,
		_config,
		_rtos,
		_timer,
		_web,
		_remoteSocket,
		_localSocket,
		_localBroadcastChannel,
		_crypt,
		_otaClient,
		_indicator,
		_nvRam,
		_log), adc(_i2c), control(_control){
	adcSemaphore = _rtos.GetSemaphore(1, 0);
	solarVoltage = 0;
	solarCurrent = 0;
	batteryVoltage = 0;
	inverterChargeCurrent = 0;
	usageCurrent = 0;
//	offsetSolarCurrent = 0;
//	offsetBatteryCurrent = 0;
	_rtos.Start(*this);
}

GreenHouseLogger::~GreenHouseLogger() {

}

uint16_t GreenHouseLogger::Read(uint8_t channel, uint8_t count){
	uint32_t sum = 0;
	for (int i = 0; i < count; i++){
		if (i == 0)
			sum += adc.ReadSingleEnded(channel);
		else
			sum += adc.GetSingleEndedResult();
	}
	return sum/count;
}

#define SOLAR_VOLTAGE 0
#define BATTERY_VOLTAGE 1
#define SOLAR_CURRENT 2
#define INVERTER_CURRENT 3

//#define SOLAR_VOLTAGE 2
//#define BATTERY_VOLTAGE 3
//#define SOLAR_CURRENT 0
//#define INVERTER_CURRENT 1

void GreenHouseLogger::Read(double& solarVoltage, double& solarCurrent, double& batteryVoltage, double& inverterCurrent){
	adcSemaphore->Take();

	double _solarVoltage = adc.Convert(Read(SOLAR_VOLTAGE));
	double _batteryVoltage = adc.Convert(Read(BATTERY_VOLTAGE));
	double _solarCurrent = adc.Convert(Read(SOLAR_CURRENT));
	double _inverterCurrent = adc.Convert(Read(INVERTER_CURRENT));

	adcSemaphore->Give();

	double __solarVoltage = (_solarVoltage - 2.5) * (100000.0/2200.0);
	if (appConfig.greenHouseReverse & 1)
		__solarVoltage = -__solarVoltage;
	double __batteryVoltage = (_batteryVoltage - 2.5) * (100000.0/2200.0);
	if (appConfig.greenHouseReverse & 2)
		__batteryVoltage = -__batteryVoltage;
	double __solarCurrent = (_solarCurrent - appConfig.greenHouseSolarCurrentRef) * (1.0 / 22e-3);
	if (appConfig.greenHouseReverse & 4)
		__solarCurrent = -__solarCurrent;
	double __inverterCurrent = (_inverterCurrent - appConfig.greenHouseInveterCurrentRef) * (1.0 / 22e-3);
	if (appConfig.greenHouseReverse & 8)
		__inverterCurrent = -__inverterCurrent;
	DBG("sv:%s,sc:%s,bv:%s,bc:%s", String(_solarVoltage).GetAddress(), String(_solarCurrent).GetAddress(), String(_batteryVoltage).GetAddress(), String(_inverterCurrent).GetAddress());
	DBG("sv:%s,sc:%s,bv:%s,bc:%s", String(__solarVoltage).GetAddress(), String(__solarCurrent).GetAddress(), String(__batteryVoltage).GetAddress(), String(__inverterCurrent).GetAddress());
//	if (fabs(__solarCurrent) < 0.5){
//		__solarCurrent = 0;
//	}
//	if (fabs(__inverterCurrent) < 0.5){
//		__inverterCurrent = 0;
//	}
	solarVoltage = fabs(__solarVoltage);
	solarCurrent = fabs(__solarCurrent);
	batteryVoltage = fabs(__batteryVoltage);
	inverterCurrent = __inverterCurrent;
}

void GreenHouseLogger::Broadcast(){
	SendLocalBroadcast(5, solarVoltage, solarCurrent, batteryVoltage, inverterChargeCurrent, usageCurrent);
}

void GreenHouseLogger::GetPublishData(PacketBuilder& packet, uint32_t userFlags){
	packet.Push(solarVoltage);
	packet.Push(solarCurrent);
	packet.Push(batteryVoltage);
	packet.Push(inverterChargeCurrent);
	packet.Push(usageCurrent);
	packet.Push(state.solarCharge);
	packet.Push(state.batteryCharge);
	packet.Push(state.inverterCharge);
	packet.Push(state.usageCharge);
	packet.Push(state.maxSolarCurrent);
	packet.Push(state.maxChargeCurrent);
	packet.Push(state.maxLoadCurrent);
	packet.Push((uint8_t)control.Read());
}

bool GreenHouseLogger::ProcessRemoteCommand(ICommChannel& channel, const String& sender, const PacketBuilder& message, PacketBuilder& response){
	uint16_t preamble = message.GetWord();
	if (preamble == 0x6732){
		uint8_t command = message.GetByte();
		switch (command){
			case 128+1:{
				uint8_t state = message.GetByte();
				control.Write(state != 0 ? IPinIO::HIGH : IPinIO::LOW);
				Publish();
				return true;
			}
			case 128+2:{ //reset energy accumulations
				state.solarCharge = 0;
				state.batteryCharge = 0;
				state.inverterCharge = 0;
				state.usageCharge = 0;
				state.maxChargeCurrent = 0;
				state.maxSolarCurrent = 0;
				state.maxLoadCurrent = 0;
				SaveState();
				Publish();
				return true;
			}
			case 128+3:{//zero reference
				adcSemaphore->Take();
				appConfig.greenHouseSolarCurrentRef = adc.Convert(Read(SOLAR_CURRENT, 64));
				appConfig.greenHouseInveterCurrentRef = adc.Convert(Read(INVERTER_CURRENT, 64));
				adcSemaphore->Give();
				appConfig.Save();
				Publish();
				return true;
			}
		}
	}
	return LoggingSmartDeviceBase<GreenState, GreenLog>::ProcessRemoteCommand(channel, sender, message, response);
}

ThreadParam GreenHouseLogger::GetThreadRequirements(){
	return ThreadParam(DEFAULT_THREAD_PRIORITY, DEFAULT_THREAD_STACK_SIZE, ROMS("logger"));
}

void GreenHouseLogger::RunThread(IThreadContext& context, int32_t message){
	TimerTick lastLogTime = 0;
	Calendar lastCalendar;
	bool firstReading = true;
	double lastLogBatteryVoltage = 0;
	double lastLogSolarVoltage = 0;
	double lastLogLoadCurrent = 0;
	double lastLogSolarCurrent = 0;
	TimerTick lastTime = timer.Get();
	while(!context.IsAborted()){
		double _batteryV, _solarV, _loadI, _solarI;
		Read(_solarV, _solarI, _batteryV, _loadI);
		TimerTick _now = timer.Get();
		if (!firstReading){ //first reading is just wrong
			batteryVoltage = _batteryV;
			solarVoltage = _solarV;
			if (_solarI < 0)
				_solarI = 0;
			solarCurrent = _solarI;
			if (_loadI < 0){
				usageCurrent = _loadI;
				inverterChargeCurrent = 0;
			} else {
				inverterChargeCurrent = _loadI;
				usageCurrent = 0;
			}
			double _batteryI = _solarI + _loadI;
//			double inverterPower = _batteryV * _inverterI;
//			double solarPower = _solarV *_solarI;
//			double batteryPower = _batteryV * _batteryI;

			double h = (_now - lastTime).Us() / (1000000.0 * 3600.0);
			if (_loadI < 0){
				state.usageCharge += h * _loadI;
			}else{
				state.inverterCharge += h * _loadI;
			}
			state.solarCharge += h * _solarI;
			state.batteryCharge += h * _batteryI;
			if (solarCurrent > state.maxSolarCurrent)
				state.maxSolarCurrent = solarCurrent;
			if (usageCurrent < state.maxLoadCurrent)
				state.maxLoadCurrent = usageCurrent;
			if (_batteryI > state.maxChargeCurrent)
				state.maxChargeCurrent = _batteryI;
			SaveState();

			Calendar now = Calendar::GetInstance();

			if (appConfig.greenHouseLogDailySummary && lastCalendar.GetTime() != 0 && now.GetDate() != lastCalendar.GetDate()){ //a new day
				GreenLog _log;
				_log.time = lastCalendar.GetTime();
				_log.type = GreenLogDaily;
				_log.solarCharge = state.solarCharge*100;
				_log.batteryCharge = state.batteryCharge*100;
				_log.inverterCharge = state.inverterCharge*100;
				_log.usageCharge = state.usageCharge*100;
				Log(_log);
				lastCalendar = now;
			}

			TimerTick nowTick = context.GetTime();

			if (	((nowTick - lastLogTime) > ITimer::Seconds(appConfig.greenHouseMinLogInterval))
						&&
					((fabs(lastLogBatteryVoltage - _batteryV) >= appConfig.greenHouseLogdV) ||
					(fabs(lastLogSolarVoltage - _solarV) >= appConfig.greenHouseLogdV) ||
					(fabs(lastLogLoadCurrent - _loadI) >= appConfig.greenHouseLogdI) ||
					(fabs(lastLogSolarCurrent - _solarI) >= appConfig.greenHouseLogdI))){
				GreenLog _log;
				_log.time = now.GetTime();
				_log.type = GreenLogInstant;
				_log.solarVoltage = _solarV * 100;
				_log.solarCurrent = _solarI * 100;
				_log.batteryVoltage = _batteryV * 100;
				if (_loadI < 0){
					_log.usageCurrent = _loadI * 100;
					_log.inverterChargeCurrent = 0;
				}else{
					_log.inverterChargeCurrent = _loadI * 100;
					_log.usageCurrent = 0;
				}
				Log(_log);
				//if (index / log.GetWritePageSize() != ((index + sizeof(LOG)) / log.GetWritePageSize()))//switching page? save index
				//	appConfig.Save();
				lastLogBatteryVoltage = _batteryV;
				lastLogSolarVoltage = _solarV;
				lastLogLoadCurrent = _loadI;
				lastLogSolarCurrent = _solarI;
				lastLogTime = nowTick;
			}
		}
		lastTime = _now;
		firstReading = false;
		context.Sleep(500);
	}
}

} /* namespace iSmart */
} /* namespace Products */
} /* namespace SAKE */
