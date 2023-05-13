using LivingThing.Core.Frameworks.Client.Interface;
using LivingThing.Core.IOT.Devices.GreenHouseLogger;
using LivingThing.Core.IOT.Devices.GreenHouseLogger.Models;
using LivingThing.Core.IOT.Common.Interface;
using LivingThing.Core.IOT.Client.ViewModels;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Text;
using System.Threading.Tasks;

namespace LivingThing.Core.IOT.Client.Devices.GreenHouseLogger.ViewModels
{
    public class GreenHouseLoggerHistoryViewModel:DeviceViewModel<GreenHouseLoggerDevice>
    {
        public GreenHouseLoggerHistoryViewModel(AppMainPageViewModel root, IIOTDeviceScope scope, GreenHouseLoggerDevice device) : base(root, scope, device)
        {
        }
    }
}
