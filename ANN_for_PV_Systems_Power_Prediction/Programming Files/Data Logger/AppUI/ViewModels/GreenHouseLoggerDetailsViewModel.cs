using LivingThing.Core.Frameworks.Client.Interface;
using LivingThing.Core.Frameworks.Common.Data;
using LivingThing.Core.Frameworks.Common.String;
using LivingThing.Core.IOT.Devices.GreenHouseLogger;
using LivingThing.Core.IOT.Devices.GreenHouseLogger.Models;
using LivingThing.Core.IOT.Devices.GreenHouseLogger.Settings;
using LivingThing.Core.IOT.Common.Interface;
using LivingThing.Core.IOT.Client.Devices;
using LivingThing.Core.IOT.Client.Devices.ViewModels;
using System;
using System.Collections.Generic;
using System.Text;
using LivingThing.Core.IOT.Client.ViewModels;

namespace LivingThing.Core.IOT.Client.Devices.GreenHouseLogger.ViewModels
{
    public class GreenHouseLoggerDetailsViewModel : DeviceDetailsViewModel<GreenHouseLoggerDevice, GreenHouseLoggerSettings, GreenHouseLoggerHardwareSettings, GreenHouseLoggerReceivedDataModel, GreenHouseLoggerControlModel>, IChartable<GreenHouseLoggerReceivedDataModel>
    {
        public GreenHouseLoggerDetailsViewModel(AppMainPageViewModel root, IIOTDeviceScope scope, GreenHouseLoggerDevice device) : base(root, scope, device)
        {
        }

        public IEnumerable<IDataPointDescriptor> Charts => new DataPointDescriptor[]
        {
            new DataPointDescriptor
            {
                Name = nameof(Device.Status.Status.SolarVoltage),
                Label = nameof(Device.Status.Status.SolarVoltage).CamelCaseToTitle()
            },
            new DataPointDescriptor
            {
                Name = nameof(Device.Status.Status.SolarCurrent),
                Label = nameof(Device.Status.Status.SolarCurrent).CamelCaseToTitle()
            },
            new DataPointDescriptor
            {
                Name = nameof(Device.Status.Status.BatteryVoltage),
                Label = nameof(Device.Status.Status.BatteryVoltage).CamelCaseToTitle()
            },
            new DataPointDescriptor
            {
                Name = nameof(Device.Status.Status.InverterChargeCurrent),
                Label = nameof(Device.Status.Status.InverterChargeCurrent).CamelCaseToTitle()
            },
            new DataPointDescriptor
            {
                Name = nameof(Device.Status.Status.UsageCurrent),
                Label = nameof(Device.Status.Status.UsageCurrent).CamelCaseToTitle()
            }
        };
    }
}
