using LivingThing.Core.IOT.Client.Devices.GreenHouseLogger.ViewModels;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Text;
using System.Collections.Specialized;
using System.Threading.Tasks;
using System.Linq;
using LivingThing.Core.Frameworks.Client.SPA;
using Microsoft.AspNetCore.Components;

namespace LivingThing.Core.IOT.Client.Devices.GreenHouseLogger.Views
{
    public partial class GreenHouseHistoryPage: ApplicationPageBaseOfViewModel<GreenHouseLoggerHistoryViewModel>
    {
        [Parameter] public override GreenHouseLoggerHistoryViewModel ViewModel { get; set; }
        //    public GreenHouseHistoryPage()
        //    {
        //        ShowTabBar = false;
        //        ShowNavBar = false;
        //    }

        //    ObservableCollection<InstantLog> InstantLogs { get; } = new ObservableCollection<InstantLog>();
        //    ObservableCollection<DailyLog> DailyLogs { get; } = new ObservableCollection<DailyLog>();
        //    ObservableCollection<Microcharts.ChartEntry> SolarVoltageEntries { get; } = new ObservableCollection<ChartEntry>();
        //    ObservableCollection<Microcharts.ChartEntry> SolarCurrentEntries { get; } = new ObservableCollection<ChartEntry>();
        //    ObservableCollection<Microcharts.ChartEntry> BatteryVoltageEntries { get; } = new ObservableCollection<ChartEntry>();
        //    ObservableCollection<Microcharts.ChartEntry> InverterCurrentEntries { get; } = new ObservableCollection<ChartEntry>();
        //    ObservableCollection<Microcharts.ChartEntry> SolarEnergyEntries { get; } = new ObservableCollection<ChartEntry>();
        //    ObservableCollection<Microcharts.ChartEntry> BatteryEnergyEntries { get; } = new ObservableCollection<ChartEntry>();
        //    ObservableCollection<Microcharts.ChartEntry> InverterEnergyEntries { get; } = new ObservableCollection<ChartEntry>();
        //    //Dictionary<Log, ChartEntry> relations = new Dictionary<Log, ChartEntry>();

        //    string SolarVoltageColor => "446622";
        //    string SolarCurrentColor => "224466";
        //    string BatteryVoltageColor => "664422";
        //    string InverterCurrentColor => "878464";

        //    string SolarEnergyColor => "446622";
        //    string BatteryEnergyColor => "224466";
        //    string InverterEnergyColor => "664422";

        //    Color ToXColor(string color) => Xamarin.Forms.Color.FromHex("#" + color);
        //    SKColor ToSkiaColor(string color) => SKColor.Parse(color);

        //    protected override void OnInitialized()
        //    {
        //        pageNumber = PageCount - 1;
        //        _ = Load();
        //        base.OnInitialized();
        //    }

        //    void OnTapped(object sender, ItemTappedEventArgs args)
        //    {
        //        ListView list = sender as ListView;
        //        list.SelectedItem = null;
        //    }

        //    bool loading = false;
        //    bool animate = true;
        //    DateTime StartDate { get; set; }
        //    string Error { get; set; }
        //    int pageNumber = 0;
        //    int PageCount => (((ViewModel.Device.Status?.LogCount ?? 0) - 1) / count) + 1;
        //    int count = 20;
        //    async Task Load()
        //    {
        //        Error = null;
        //        loading = true;
        //        //animate = true;
        //        try
        //        {
        //            int start = pageNumber * count;
        //            int cnt = count;
        //            if (start+count > (ViewModel.Device.Status?.LogCount ?? int.MaxValue))
        //            {
        //                cnt = ViewModel.Device.Status.LogCount - start;
        //            }
        //            var logs = await ViewModel.Device.ReadLogs(start, cnt);
        //            //Random r = new Random();
        //            //var logs = new List<Log>();
        //            //for (int i = 0; i < count; i++)
        //            //{
        //            //    logs.Add(new Log() { 
        //            //        BatteryVoltage = r.NextDouble(),
        //            //        SolarCurrent = r.NextDouble(),
        //            //        SolarVoltage = r.NextDouble(),
        //            //        InverterCurrent = r.NextDouble(),
        //            //        Time = DateTime.UtcNow                    
        //            //    });
        //            //}
        //            //var logs = new Log[] { 
        //            //    new Log(){ BatteryVoltage = r.NextDouble()}
        //            //};
        //            int ii = 0;
        //            SolarVoltageEntries.Clear();
        //            SolarCurrentEntries.Clear();
        //            BatteryVoltageEntries.Clear();
        //            InverterCurrentEntries.Clear();
        //            SolarEnergyEntries.Clear();
        //            BatteryEnergyEntries.Clear();
        //            InverterEnergyEntries.Clear();
        //            foreach (var log in logs)
        //            {
        //                if (ii == 0)
        //                    StartDate = log.Time;
        //                if (log is InstantLog ilog)
        //                {
        //                    if (!InstantLogs.Any(il => il.Equals(log)))
        //                    {
        //                        InstantLogs.Add(ilog);
        //                    }
        //                    var solarVoltageEntry = new Microcharts.ChartEntry((float)ilog.SolarVoltage)
        //                    {
        //                        Label = ilog.Time.ToString("HH:mm"),
        //                        ValueLabel = ilog.SolarVoltage.ToString("f"),
        //                        Color = ToSkiaColor(SolarVoltageColor),
        //                        TextColor = ToSkiaColor(SolarVoltageColor)
        //                    };
        //                    SolarVoltageEntries.Add(solarVoltageEntry);

        //                    var solarCurrentEntry = new Microcharts.ChartEntry((float)ilog.SolarCurrent)
        //                    {
        //                        Label = ilog.Time.ToString("HH:mm"),
        //                        ValueLabel = ilog.SolarCurrent.ToString("f"),
        //                        Color = ToSkiaColor(SolarCurrentColor),
        //                        TextColor = ToSkiaColor(SolarCurrentColor)
        //                    };
        //                    SolarCurrentEntries.Add(solarCurrentEntry);

        //                    var batteryVoltageEntry = new Microcharts.ChartEntry((float)ilog.BatteryVoltage)
        //                    {
        //                        Label = ilog.Time.ToString("HH:mm"),
        //                        ValueLabel = ilog.BatteryVoltage.ToString("f"),
        //                        Color = ToSkiaColor(BatteryVoltageColor),
        //                        TextColor = ToSkiaColor(BatteryVoltageColor)
        //                    };
        //                    BatteryVoltageEntries.Add(batteryVoltageEntry);

        //                    var loadCurrentEntry = new Microcharts.ChartEntry((float)ilog.InverterCurrent)
        //                    {
        //                        Label = ilog.Time.ToString("HH:mm"),
        //                        ValueLabel = ilog.InverterCurrent.ToString("f"),
        //                        Color = ToSkiaColor(InverterCurrentColor),
        //                        TextColor = ToSkiaColor(InverterCurrentColor)
        //                    };
        //                    InverterCurrentEntries.Add(loadCurrentEntry);
        //                    //relations[log] = entry;
        //                }
        //                else if (log is DailyLog dlog)
        //                {
        //                    if (!DailyLogs.Any(il => il.Equals(log)))
        //                    {
        //                        DailyLogs.Add(dlog);
        //                    }
        //                    var solarEnergyEntry = new Microcharts.ChartEntry((float)dlog.SolarEnergy)
        //                    {
        //                        Label = dlog.Time.ToString("d/M/yyyy"),
        //                        ValueLabel = dlog.SolarEnergy.ToString("f"),
        //                        Color = ToSkiaColor(SolarEnergyColor),
        //                        TextColor = ToSkiaColor(SolarEnergyColor)
        //                    };
        //                    SolarEnergyEntries.Add(solarEnergyEntry);

        //                    var batteryEnergyEntry = new Microcharts.ChartEntry((float)dlog.BatteryEnergy)
        //                    {
        //                        Label = dlog.Time.ToString("d/M/yyyy"),
        //                        ValueLabel = dlog.BatteryEnergy.ToString("f"),
        //                        Color = ToSkiaColor(BatteryEnergyColor),
        //                        TextColor = ToSkiaColor(BatteryEnergyColor)
        //                    };
        //                    BatteryEnergyEntries.Add(batteryEnergyEntry);

        //                    var inverterEnergyEntry = new Microcharts.ChartEntry((float)dlog.InverterEnergy)
        //                    {
        //                        Label = dlog.Time.ToString("d/M/yyyy"),
        //                        ValueLabel = dlog.InverterEnergy.ToString("f"),
        //                        Color = ToSkiaColor(InverterEnergyColor),
        //                        TextColor = ToSkiaColor(InverterEnergyColor)
        //                    };
        //                    InverterEnergyEntries.Add(inverterEnergyEntry);
        //                }
        //                ii++;
        //            }
        //            var dlogs = DailyLogs.OrderBy(l => l.Time).ToArray();
        //            DailyLogs.Clear();
        //            foreach (var dlog in dlogs)
        //            {
        //                DailyLogs.Add(dlog);
        //            }
        //            var ilogs = InstantLogs.OrderBy(l => l.Time).ToArray();
        //            InstantLogs.Clear();
        //            foreach (var ilog in ilogs)
        //            {
        //                InstantLogs.Add(ilog);
        //            }
        //        }
        //        finally
        //        {
        //            loading = false;
        //            await StateChanged();
        //            animate = false;//disable subsequent animation
        //        }
        //    }

        //    async Task NextPage()
        //    {
        //        if (pageNumber < PageCount - 1)
        //        {
        //            try
        //            {
        //                pageNumber++;
        //                await Load();
        //            }catch(Exception e)
        //            {
        //                Error = e.Message;
        //                pageNumber--;
        //            }
        //        }
        //    }

        //    async Task PreviousPage()
        //    {
        //        if (pageNumber > 0)
        //        {
        //            try
        //            {
        //                pageNumber--;
        //                await Load();
        //            }
        //            catch (Exception e)
        //            {
        //                Error = e.Message;
        //                pageNumber++;
        //            }
        //        }
        //    }
    }
}
