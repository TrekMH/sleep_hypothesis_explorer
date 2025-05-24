import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

def sleep_homeostasis_simulation(
    peak_time=4.0, 
    h_c_ratio=1.0, 
    bedtime=23.0, 
    waketime=6.0, 
    circadian_waveform='behavioral alertness - wake maintenance zone',
    H0 = 0.05,
    Hmax=1,
    SleepEff=0.5,
    timezone_shift=0,  # in hours
    annotation=None  # new optional annotation string
):
    def hours_to_ampm(hour_float):
        hour_float = hour_float % 24
        hours = int(hour_float)
        minutes = int(round((hour_float - hours) * 60))
        if minutes == 60:
            minutes = 0
            hours = (hours + 1) % 24
        ampm = "AM" if hours < 12 or hours == 24 else "PM"
        display_hour = hours % 12
        display_hour = 12 if display_hour == 0 else display_hour
        return f"{display_hour}:{minutes:02d} {ampm}"

    # def circadian_phase_from_peak(peak_hour):
    #     return (np.pi / 2) - (2 * np.pi * peak_hour / 24)

    def is_sleep(hour):
        if bedtime < waketime:
            return bedtime <= hour < waketime
        else:
            return hour >= bedtime or hour < waketime

    def is_work(hour):
        return 9 <= hour < 17

    # Time parameters
    dt = 0.1
    T = 72
    time = np.arange(0, T, dt)
    internal_time = (time + 6) % 24  # 0 = 6 AM
    local_time = (internal_time + timezone_shift) % 24  # local clock time

    # Parameters
    tau_rise = 30
    tau_decay = 2/np.max([1e-16,SleepEff])
    circadian_period = 24
    circadian_amplitude = 0.2
    # circadian_phase = circadian_phase_from_peak(peak_time)
    circadian_phase = 2 * np.pi * peak_time / circadian_period  # cosinor phase

    base_threshold_sleep = 0.85

    H = np.zeros_like(time)
    C = np.zeros_like(time)
    state = np.zeros_like(time)
    # threshold_sleep = np.zeros_like(time)

    H[0] = H0

    # # Generate circadian waveform
    # if circadian_waveform == 'classic - cosinor':
    #     C = circadian_amplitude * np.cos(2 * np.pi * real_time / circadian_period - circadian_phase)
    # elif circadian_waveform == 'behavioral alertness - wake maintenance zone':
    #     # Use peak_time argument to set peak hour
    #     width = 17 / 24  # 17-hour descent from peak to trough
    #     phase_shift = -2 * np.pi * peak_time / circadian_period
    #     C = -circadian_amplitude * signal.sawtooth(
    #         2 * np.pi * real_time / circadian_period + phase_shift,
    #         width=width
    #     )
    # else:
    #     raise ValueError("circadian_waveform must be 'cosinor' or 'sawtooth'")

    if circadian_waveform == 'classic - cosinor':
        C = circadian_amplitude * np.cos(2 * np.pi * internal_time / circadian_period - circadian_phase)
    elif circadian_waveform == 'behavioral alertness - wake maintenance zone':
        width = 17 / 24
        phase_shift = -2 * np.pi * peak_time / circadian_period
        C = -circadian_amplitude * signal.sawtooth(
            2 * np.pi * internal_time / circadian_period + phase_shift,
            width=width
        )



    # for i in range(1, len(time)):
    #     hour = real_time[i]
    #     state[i] = 1 if is_sleep(hour) else 0
    #     # threshold_sleep[i] = base_threshold_sleep + C[i]
    #     dH = ((Hmax - H[i-1]) / tau_rise if state[i] == 0 else -H[i-1] / tau_decay) * dt
    #     H[i] = H[i-1] + dH

    for i in range(1, len(time)):
        hour = local_time[i]
        state[i] = 1 if is_sleep(hour) else 0
        # threshold_sleep[i] = base_threshold_sleep + C[i]
        dH = ((Hmax - H[i-1]) / tau_rise if state[i] == 0 else -H[i-1] / tau_decay) * dt
        H[i] = H[i-1] + dH


    net_sleep_pressure = h_c_ratio/2*H + (1-h_c_ratio/2)*C

    # Compute work mask over the full time range
    work_mask = np.array([is_work(hr) for hr in local_time])

    # Calculate average net sleep pressure during work hours
    if np.any(work_mask):
        avg_work_pressure = np.mean(net_sleep_pressure[work_mask])
    else:
        avg_work_pressure = np.nan  # Handle edge case if no work hours in the simulation

    # Optionally print or include it in the summary text
    print(f"Average Net Sleep Pressure during Work: {avg_work_pressure:.3f}")

    # Plotting
    plt.figure(figsize=(12, 12))
    plt.plot(time, h_c_ratio/2*H , label='Homeostatic Sleep Pressure (H)', color='blue',linestyle="--", lw=4,alpha=0.8)
    plt.plot(time, (1-h_c_ratio/2)*C, label=f'Circadian-Fatigue Drive (C)', color='orange',linestyle="--", lw=4,alpha=0.8)
    plt.plot(time, net_sleep_pressure, label=r'Fatigue (Alertness$^{-1}$)', color='purple',lw=8)
    # Mask net_sleep_pressure during sleep periods
    # masked_net_pressure = np.where(np.array([is_sleep(hr) for hr in local_time]), np.nan, net_sleep_pressure)

    # # Plot only during wake
    # plt.plot(time, masked_net_pressure, label=r'Fatigue (Alertness$^{-1}$)', color='purple', lw=8)

    # sleep_mask = np.array([is_sleep(hr) for hr in real_time])
    # work_mask = np.array([is_work(hr) for hr in real_time])

    sleep_mask = np.array([is_sleep(hr) for hr in local_time])
    work_mask = np.array([is_work(hr) for hr in local_time])



    plt.fill_between(time, -0.5, Hmax, where=sleep_mask, color='skyblue', alpha=0.3, label='Forced Sleep Period')
    plt.fill_between(time, -0.5, Hmax, where=work_mask, color='orangered', alpha=0.3, label='Performance Period')

    # for day_start in range(0, int(T), 24):
    #     plt.axvline(day_start + (9 - 6), color='orange', linestyle='--', alpha=0.7)
    #     plt.axvline(day_start + (17 - 6), color='orange', linestyle='--', alpha=0.7)

    tick_hours = np.arange(0, T+1, 4)
    # tick_labels = [hours_to_ampm((h + 6) % 24) for h in tick_hours]
    tick_labels = [hours_to_ampm(lt) for lt in (tick_hours + 6 + timezone_shift) % 24]

    plt.xticks(tick_hours, tick_labels, rotation=90)
    plt.xlabel('Time (AM/PM)')
    plt.ylabel('Pressure / Drive')
    plt.title('Sleep Homeostasis with Circadian Drive and Behavioral Schedule')
    plt.ylim([-0.5, Hmax])
    plt.legend()
    plt.grid(True)


    summary_text = (
        f"Performance Metrics:\n"
        f"Avg Net Pressure (Work): {avg_work_pressure:.3f}\n"
        f"\nParameters:\n"
        f"Time Zone: {'HOME' if timezone_shift == 0 else f'{timezone_shift:+} hr'}\n"
        f"Circadian-Fatigue Peak Time: {peak_time} hr\n"
        f"Bedtime: {bedtime} hr\n"
        f"Waketime: {waketime} hr\n"
        f"Sleep Efficiency: {SleepEff} (0-1)\n"
        f"H/C Ratio: {h_c_ratio}\n"
        f"Circadian Waveform:\n{circadian_waveform}\n"
    
    )
    if annotation:
        summary_text += f"\nNote: {annotation}"

    # Put summary text on right side of plot, vertically centered
    plt.text(
        0, -1,  # x, y coordinates in data coords (adjust as needed)
        summary_text,
        fontsize=16,
        verticalalignment='center',
        bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.5')
    )

    # Instead of plt.show(), just return the figure:
    fig = plt.gcf()
    plt.close(fig)
    return fig

