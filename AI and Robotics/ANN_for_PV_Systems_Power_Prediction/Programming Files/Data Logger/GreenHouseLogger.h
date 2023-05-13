/*
 * GreenHouseLogger.h
 *
 *  Created on: Aug 26, 2020
 *      Author: ojesc
 */

#ifndef SRC_DEVICES_GREENHOUSELOGGER_GREENHOUSELOGGER_H_
#define SRC_DEVICES_GREENHOUSELOGGER_GREENHOUSELOGGER_H_

#include <Devices/Base/SmartDeviceBase.h>
#include <Devices/ADS1X15/ADS1X15.h>
#include <Contracts/S@IPersistence.hpp>
#include <Contracts/RTOS/S@IRTOSController.h>

namespace SAKE {
namespace Products {
namespace iSmart {

using namespace SAKE::Library::Contracts;
using namespace SAKE::Library::Devices;
using namespace SAKE::Library::Infrastructures;

struct GreenState:State {
	double solarCharge;
	double batteryCharge;
	double inverterCharge;
	double usageCharge;
	double maxSolarCurrent;
	double maxChargeCurrent;
	double maxLoadCurrent;
};

enum GreenLogType{
	GreenLogInstant,
	GreenLogDaily
};

struct PACKED GreenLog{
	uint8_t type;
	uint32_t time;
	union{
		struct{
			int16_t solarVoltage;
			int16_t solarCurrent;
			int16_t batteryVoltage;
			int16_t usageCurrent;
			int16_t inverterChargeCurrent;
		};
		struct{
			int32_t solarCharge;
			int32_t batteryCharge;
			int32_t inverterCharge;
			int32_t usageCharge;
		};
	};
	operator Array_<uint8_t>(){
		PacketBuilder packet;
		packet.Push(type);
		packet.Push(time);
		if (type == GreenLogInstant){
			packet.Push(solarVoltage);
			packet.Push(solarCurrent);
			packet.Push(batteryVoltage);
			packet.Push(usageCurrent);
			packet.Push(inverterChargeCurrent);
		}else{
			packet.Push(solarCharge);
			packet.Push(batteryCharge);
			packet.Push(inverterCharge);
			packet.Push(usageCharge);
		}
		return Array_<uint8_t>(packet.GetBuffer(), packet.GetLength());
	}
};

class GreenHouseLogger: public LoggingSmartDeviceBase<GreenState, GreenLog>, IThread {
public:
	GreenHouseLogger(AppConfig& _appConfig,
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
			IPinOutput& _control);
	virtual ~GreenHouseLogger();
	void GetPublishData(PacketBuilder& packet, uint32_t userFlags);
	void Broadcast();

	bool ProcessRemoteCommand(ICommChannel& channel, const String& sender, const PacketBuilder& message, PacketBuilder& response);

	ThreadParam GetThreadRequirements();
	void RunThread(IThreadContext& context, int32_t message = 0);
private:
	GreenState state;
	State& GetState(){ return state; }
	uint16_t Read(uint8_t channel, uint8_t count = 16);
	void Read(double& solarVoltage, double& solarCurrent, double& batteryVoltage, double& inverterCurrent);
	void GetData(PacketBuilder& packet, bool includeId = false);
	ISemaphore* adcSemaphore;
	ADS1X15 adc;
	IPinOutput& control;
//	double offsetSolarCurrent;
//	double offsetBatteryCurrent;
	double solarVoltage;
	double solarCurrent;
	double batteryVoltage;
	double inverterChargeCurrent;
	double usageCurrent;
};

} /* namespace iSmart */
} /* namespace Products */
} /* namespace SAKE */

#endif /* SRC_DEVICES_GREENHOUSELOGGER_GREENHOUSELOGGER_H_ */
