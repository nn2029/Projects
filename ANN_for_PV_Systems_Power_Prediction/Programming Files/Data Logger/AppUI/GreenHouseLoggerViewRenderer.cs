using LivingThing.Core.Frameworks.Client;
using LivingThing.Core.Frameworks.Client.Interface;
using LivingThing.Core.IOT.Devices.GreenHouseLogger;
using LivingThing.Core.IOT.Devices.GreenHouseLogger.Models;
using LivingThing.Core.IOT.Devices.GreenHouseLogger.Settings;
using LivingThing.Core.IOT.Interface.Client;
using LivingThing.Core.IOT.Client.Devices.GreenHouseLogger.ViewModels;
using LivingThing.Core.IOT.Client.Devices.GreenHouseLogger.Views;
using LivingThing.Core.IOT.Client.Devices.ViewModels;
using LivingThing.Core.IOT.Client.ViewModels;
using Microsoft.AspNetCore.Components;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace LivingThing.Core.IOT.Client.Devices.GreenHouseLogger
{
    public class GreenHouseLoggerViewRenderer:DeviceViewRenderer<GreenHouseLoggerDevice, GreenHouseLoggerSettings, GreenHouseLoggerHardwareSettings, GreenHouseLoggerReceivedDataModel, GreenHouseLoggerControlModel>, IViewProvider<InstantLog>
    {
        public GreenHouseLoggerViewRenderer(AppMainPageViewModel root) : base(root)
        {
        }

        public override RenderFragment GetView(IUIService ui, GreenHouseLoggerDevice device, DeviceViewType type, Func<int, Task> clicked = null, Func<Task> pressed = null)
        {
            if (type == DeviceViewType.Details)
            {
                return FragmentView.From<GreenHouseLoggerDeviceDetails, GreenHouseLoggerDetailsViewModel>(new GreenHouseLoggerDetailsViewModel(Root, device.OwnerScope, device), true);
            }
            return base.GetView(ui, device, type, clicked, pressed);
        }

        public RenderFragment GetView(ContainerContext<InstantLog> value)
        {
            return FragmentView.From<GreenHouseInstantLog>(new Dictionary<String, object>()
            {
                [nameof(GreenHouseInstantLog.ViewModel)] = value.Model
            });
        }
    }
}
