import streamlit as st
from sleep_system import sleep_homeostasis_simulation
import io

st.title("Sleep Homeostasis Simulation")

tz_shift = st.slider("TZ shift", -12, 12, 0)
peak_time = st.slider("Circadian-Fatigue Peak Time (hr)", 0, 24, 4)
bedtime = st.slider("Bedtime", 0.0, 24.0, 23.0)
waketime = st.slider("Waketime", 0.0, 24.0, 6.0)
SleepEff = st.slider("Sleep Efficiency", 0.0, 1.0, 0.5)
H0 = st.slider("Initial Homeostasis", 0.0, 1.0, 0.05)
h_c_ratio = st.slider("H/C ratio", 0.0, 2.0, 1.0)
waveform = st.selectbox("Circadian Waveform", ["behavioral alertness - wake maintenance zone","classic - cosinor"])
annotation = st.text_input("Optional short annotation/note")

# if st.button("Run Simulation"):
#     fig = sleep_homeostasis_simulation(
#         peak_time=peak_time,
#         h_c_ratio=h_c_ratio,
#         bedtime=bedtime,
#         waketime=waketime,
#         H0 = H0,
#         SleepEff=SleepEff,
#         circadian_waveform=waveform,
#         timezone_shift=tz_shift,
#         annotation=annotation
#     )
    
#     st.pyplot(fig)
    
    # buf = io.BytesIO()
    # fig.savefig(buf, format="png")
    # buf.seek(0)
    # st.download_button(
    #     label="Download Plot as PNG",
    #     data=buf,
    #     file_name="sleep_simulation.png",
    #     mime="image/png"
    # )
if "fig" not in st.session_state:
    st.session_state.fig = None

if st.button("Run Simulation"):
    fig = sleep_homeostasis_simulation(
        peak_time=peak_time,
        h_c_ratio=h_c_ratio,
        bedtime=bedtime,
        waketime=waketime,
        H0=H0,
        SleepEff=SleepEff,
        circadian_waveform=waveform,
        timezone_shift=tz_shift,
        annotation=annotation
    )
    st.session_state.fig = fig  # store in session state

# Always show if figure exists
if st.session_state.fig is not None:
    st.pyplot(st.session_state.fig)

    buf = io.BytesIO()
    st.session_state.fig.savefig(buf, format="png", bbox_inches='tight', pad_inches=0.2)
    buf.seek(0)
    st.download_button(
        label="Download Plot as PNG",
        data=buf,
        file_name=f"sleep_simulation_{annotation}.png",
        mime="image/png"
    )
st.session_state.fig = None


## CASES
## Circadian delay (shifts)
## TZ Change
## Sleep Loss