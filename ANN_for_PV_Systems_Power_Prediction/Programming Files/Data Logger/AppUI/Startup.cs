using LivingThing.Core.Frameworks.Common.Requests;
using LivingThing.Core.Frameworks.Common;
using LivingThing.Core.IOT.Devices.GreenHouseLogger;
using LivingThing.Core.IOT.Interface.Client;
using Microsoft.Extensions.DependencyInjection;
using System.Collections.Generic;
using System.Text;
using LivingThing.Core.Frameworks.Client;
using LivingThing.Core.IOT.Client.Devices.GreenHouseLogger.Views;
using LivingThing.Core.IOT.Devices.GreenHouseLogger.Models;
using LivingThing.Core.Frameworks.Client.Interface;

namespace LivingThing.Core.IOT.Client.Devices.GreenHouseLogger
{
    public static class Startup
    {
        public static void AddGreenHouseLoggerViews(this IServiceCollection services)
        {
            services.AddScoped<GreenHouseLoggerViewRenderer>()
                .AddScoped<IDeviceViewRenderer<GreenHouseLoggerDevice>>(x => x.GetRequiredService<GreenHouseLoggerViewRenderer>())
                .AddScoped<IViewProvider<InstantLog>>(x => x.GetRequiredService<GreenHouseLoggerViewRenderer>());
            //services.AddParameterizedView<GreenHouseLoggerLog, GreenHouseLoggerLogView>();
        }
    }
}
