using LivingThing.Core.Frameworks.Client.SPA;
using LivingThing.Core.Frameworks.Client.Components.Charts;
using LivingThing.Core.IOT.Devices.GreenHouseLogger.Models;
using LivingThing.Core.IOT.Client.Devices.GreenHouseLogger.ViewModels;
using Microsoft.AspNetCore.Components;
using System;
using System.Collections.Generic;
using System.Text;
using System.ComponentModel;

namespace LivingThing.Core.IOT.Client.Devices.GreenHouseLogger.Views
{
    public partial class GreenHouseLoggerDeviceDetails:ApplicationPageBaseOfViewModel<GreenHouseLoggerDetailsViewModel>
    {
        [Parameter] public override GreenHouseLoggerDetailsViewModel ViewModel { get; set; }
    }
}
