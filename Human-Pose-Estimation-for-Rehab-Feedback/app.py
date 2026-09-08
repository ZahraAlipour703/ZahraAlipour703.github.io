
# import streamlit as st
# import json, os, time
# import pandas as pd
# from run_local import run_exercise_live

# # ===============================
# # CONFIG & PATHS
# # ===============================
# CFG_PATH = r"D:\zra\PROJECTS\internship_astro\rehab-eercises\Rahabilities-General\config.json"
# LOG_PATH = r"D:\zra\PROJECTS\internship_astro\rehab-eercises\Rahabilities-General\logs"

# st.set_page_config(page_title="Rehab Monitor - Doctor UI", layout="wide")
# st.title("🏥 Rehab Monitor — Doctor Panel")

# if not os.path.exists(CFG_PATH):
#     st.error("❌ config.json not found. Please ensure it exists.")
#     st.stop()

# with open(CFG_PATH, "r", encoding="utf-8") as f:
#     cfg = json.load(f)

# # ===============================
# # HELPER FUNCTIONS
# # ===============================
# def get_default(section, key, default):
#     state_key = f"{section}_{key}"
#     if state_key in st.session_state:
#         return st.session_state[state_key]
#     value = cfg.get(section, {}).get(key, default)
#     st.session_state[state_key] = value
#     return value

# def save_cfg(section, **kwargs):
#     cfg[section] = kwargs
#     for k,v in kwargs.items():
#         st.session_state[f"{section}_{k}"] = v
#     with open(CFG_PATH, "w", encoding="utf-8") as f:
#         json.dump(cfg, f, indent=2)
#     st.success(f"✅ {section.replace('_',' ').title()} settings saved!")

# # ===============================
# # SIDEBAR — SESSION CONTROL
# # ===============================
# exercise_name = st.sidebar.selectbox(
#     "Select Exercise",
#     ["shoulder_flexion","arm_raise_and_carry","mini_squat","wall_calf_stretch",
#      "straight_leg_raise","kettlebell_swings","seated_hip_internal_rotation",
#      "farmers_carry","bodyweight_deadlift","single_leg_stance","tandem_walk"]
# )

# st.sidebar.markdown("---")
# start_live = st.sidebar.button("▶ Start Live Session")
# stop_live = st.sidebar.button("⏹ Stop Session")
# st.session_state['stop_live'] = False

# # ===============================
# # EXERCISE PANELS
# # ===============================
# def shoulder_flexion_panel():
#     st.subheader("Shoulder Flexion Settings")
#     side = st.selectbox("Side", ["both","right","left"], index=["both","right","left"].index(get_default("shoulder_flexion","side","both")))
#     target_up = st.slider("Target angle UP", 120, 180, int(get_default("shoulder_flexion","target_angle_up",160)))
#     target_down = st.slider("Target angle DOWN", 0, 90, int(get_default("shoulder_flexion","target_angle_down",40)))
#     tol = st.slider("Tolerance (deg)", 5, 30, int(get_default("shoulder_flexion","tolerance_deg",12)))
#     hold = st.slider("Hold time (sec)", 0.5,5.0,float(get_default("shoulder_flexion","hold_time_sec",1.5)))
#     if st.button("💾 Save Shoulder Flexion"):
#         save_cfg("shoulder_flexion", side=side, target_angle_up=target_up,
#                  target_angle_down=target_down, tolerance_deg=tol, hold_time_sec=hold)

# def arm_raise_panel():
#     st.subheader("Arm Raise + Carry Settings")
#     side = st.selectbox("Side", ["both","right","left"], index=["both","right","left"].index(get_default("arm_raise_and_carry","side","both")))
#     target_up = st.slider("Target angle UP", 120,180,int(get_default("arm_raise_and_carry","target_angle_up",160)))
#     target_down = st.slider("Target angle DOWN",0,90,int(get_default("arm_raise_and_carry","target_angle_down",40)))
#     hold = st.slider("Hold time (sec)",0.5,5.0,float(get_default("arm_raise_and_carry","hold_time_sec",1.5)))
#     carry_dur = st.slider("Carry duration (sec)",5,120,int(get_default("arm_raise_and_carry","carry_duration_sec",20)))
#     carry_frac = st.slider("Carry OK fraction (%)",50,100,int(get_default("arm_raise_and_carry","carry_min_ok_fraction",0.9)*100))
#     if st.button("💾 Save Arm Raise + Carry"):
#         save_cfg("arm_raise_and_carry", side=side, target_angle_up=target_up,
#                  target_angle_down=target_down, hold_time_sec=hold,
#                  carry_duration_sec=carry_dur, carry_min_ok_fraction=carry_frac/100)

# def mini_squat_panel():
#     st.subheader("Mini Squat Settings")
#     side = st.selectbox("Side", ["both","left","right"], index=["both","left","right"].index(get_default("mini_squat","side","both")))
#     down = st.slider("Down Knee Angle",40,120,int(get_default("mini_squat","down_knee_angle_deg",60)))
#     up = st.slider("Up Knee Angle",120,180,int(get_default("mini_squat","up_knee_angle_deg",170)))
#     tilt = st.slider("Max Torso Tilt",0,30,int(get_default("mini_squat","max_torso_tilt_deg",18)))
#     heel = st.slider("Heel Lift Threshold",0,15,int(get_default("mini_squat","heel_lift_thresh_deg",6)))
#     smooth = st.slider("Smoothing Window",1,10,int(get_default("mini_squat","smoothing_window",5)))
#     if st.button("💾 Save Mini Squat"):
#         save_cfg("mini_squat", side=side, down_knee_angle_deg=down, up_knee_angle_deg=up,
#                  max_torso_tilt_deg=tilt, heel_lift_thresh_deg=heel, smoothing_window=smooth)

# def wall_calf_panel():
#     st.subheader("Wall Calf Stretch Settings")
#     side = st.selectbox("Side", ["both","left","right"], index=["both","left","right"].index(get_default("wall_calf_stretch","side","both")))
#     ankle = st.slider("Ankle Stretch Threshold",150,180,int(get_default("wall_calf_stretch","ankle_stretch_thresh_deg",170)))
#     wrist = st.slider("Wrist Stretch Threshold",120,180,int(get_default("wall_calf_stretch","wrist_stretch_thresh_deg",150)))
#     arm = st.slider("Arm Straightness (deg)",120,180,int(get_default("wall_calf_stretch","arm_straight_thresh_deg",160)))
#     tol = st.slider("Tolerance",1,15,int(get_default("wall_calf_stretch","tolerance_deg",6)))
#     if st.button("💾 Save Wall Calf Stretch"):
#         save_cfg("wall_calf_stretch", side=side, ankle_stretch_thresh_deg=ankle,
#                  wrist_stretch_thresh_deg=wrist, arm_straight_thresh_deg=arm, tolerance_deg=tol)

# def straight_leg_panel():
#     st.subheader("Straight Leg Raise Settings")
#     target = st.slider("Target Angle (deg)",30,120,int(get_default("straight_leg_raise","target_up_angle",70)))
#     tol = st.slider("Tolerance (deg)",5,30,int(get_default("straight_leg_raise","tolerance_deg",10)))
#     hold = st.slider("Hold Time (sec)",0.5,5.0,float(get_default("straight_leg_raise","hold_time_sec",1.5)))
#     if st.button("💾 Save Straight Leg Raise"):
#         save_cfg("straight_leg_raise", target_up_angle=target, tolerance_deg=tol, hold_time_sec=hold)

# def kettlebell_panel():
#     st.subheader("Kettlebell Swings Settings")
#     swing = st.slider("Swing Range Angle",60,180,int(get_default("kettlebell_swings","swing_angle_deg",120)))
#     tilt = st.slider("Max Torso Tilt",0,40,int(get_default("kettlebell_swings","max_torso_tilt_deg",20)))
#     tol = st.slider("Rep Tolerance",1,15,int(get_default("kettlebell_swings","rep_tolerance_deg",6)))
#     if st.button("💾 Save Kettlebell Swings"):
#         save_cfg("kettlebell_swings", swing_angle_deg=swing, max_torso_tilt_deg=tilt, rep_tolerance_deg=tol)

# def seated_hip_panel():
#     st.subheader("Seated Hip Internal Rotation Settings")
#     target = st.slider("Target Rotation (deg)",10,90,int(get_default("seated_hip_internal_rotation","target_angle_deg",40)))
#     tol = st.slider("Tolerance (deg)",1,15,int(get_default("seated_hip_internal_rotation","tolerance_deg",5)))
#     if st.button("💾 Save Seated Hip Internal Rotation"):
#         save_cfg("seated_hip_internal_rotation", target_angle_deg=target, tolerance_deg=tol)

# def farmers_carry_panel():
#     st.subheader("Farmer's Carry Settings")
#     dur = st.slider("Carry Duration (sec)",5,120,int(get_default("farmers_carry","carry_duration_sec",20)))
#     frac = st.slider("Min Success Fraction (%)",50,100,int(get_default("farmers_carry","carry_min_ok_fraction",0.9)*100))
#     if st.button("💾 Save Farmer's Carry"):
#         save_cfg("farmers_carry", carry_duration_sec=dur, carry_min_ok_fraction=frac/100)

# def bodyweight_deadlift_panel():
#     st.subheader("Bodyweight Deadlift Settings")
#     max_tilt = st.slider("Max Torso Tilt (deg)",0,40,int(get_default("bodyweight_deadlift","max_torso_tilt_deg",25)))
#     if st.button("💾 Save Bodyweight Deadlift"):
#         save_cfg("bodyweight_deadlift", max_torso_tilt_deg=max_tilt)

# def single_leg_panel():
#     st.subheader("Single Leg Stance Settings")
#     duration = st.slider("Min Hold Duration (sec)",1,60,int(get_default("single_leg_stance","min_hold_sec",15)))
#     sway_tol = st.slider("Max Sway (deg)",0,20,int(get_default("single_leg_stance","max_sway_deg",10)))
#     if st.button("💾 Save Single Leg Stance"):
#         save_cfg("single_leg_stance", min_hold_sec=duration, max_sway_deg=sway_tol)

# def tandem_walk_panel():
#     st.subheader("Tandem Walk Settings")
#     step_len = st.slider("Step Length (cm)",20,80,int(get_default("tandem_walk","step_length_cm",50)))
#     sway_tol = st.slider("Max Sway (deg)",0,20,int(get_default("tandem_walk","max_sway_deg",10)))
#     if st.button("💾 Save Tandem Walk"):
#         save_cfg("tandem_walk", step_length_cm=step_len, max_sway_deg=sway_tol)

# exercise_panels = {
#     "shoulder_flexion": shoulder_flexion_panel,
#     "arm_raise_and_carry": arm_raise_panel,
#     "mini_squat": mini_squat_panel,
#     "wall_calf_stretch": wall_calf_panel,
#     "straight_leg_raise": straight_leg_panel,
#     "kettlebell_swings": kettlebell_panel,
#     "seated_hip_internal_rotation": seated_hip_panel,
#     "farmers_carry": farmers_carry_panel,
#     "bodyweight_deadlift": bodyweight_deadlift_panel,
#     "single_leg_stance": single_leg_panel,
#     "tandem_walk": tandem_walk_panel
# }

# if exercise_name in exercise_panels:
#     exercise_panels[exercise_name]()

# # ===============================
# # LIVE SESSION STREAM
# # ===============================
# if start_live:
#     st.session_state['stop_live'] = False
#     st.sidebar.success(f"Launching live session for '{exercise_name}'...")
#     frame_placeholder = st.empty()

#     for frame, res in run_exercise_live(exercise_name):
#         if st.session_state.get('stop_live'):
#             break
#         frame_placeholder.image(frame, channels="BGR")
#         if isinstance(res, dict):
#             if "reps" in res: st.write(f"Reps: {res['reps']}")
#             if "stage" in res: st.write(f"Stage: {res['stage']}")
#             if "feedback" in res: st.write("Feedback:", ", ".join(res["feedback"]))

# if stop_live:
#     st.session_state['stop_live'] = True
#     st.sidebar.warning("⏹ Live session stopped by doctor.")

# # ===============================
# # SESSION LOGS DISPLAY
# # ===============================
# st.markdown("---")
# st.header("📊 Session Logs")
# if os.path.exists(LOG_PATH):
#     all_csvs = [f for f in os.listdir(LOG_PATH) if f.endswith(".csv")]
#     for f in all_csvs:
#         st.markdown(f"**{f}**")
#         df = pd.read_csv(os.path.join(LOG_PATH,f), on_bad_lines='skip')
#         st.dataframe(df.tail(100))
#         st.download_button(f"⬇️ Download {f}", data=df.to_csv(index=False), file_name=f)
# else:
#     st.info("Logs folder not found.")
#---
# import streamlit as st
# import json, os, time
# import pandas as pd
# from run_local import run_exercise_live

# # ===============================
# # CONFIG & PATHS
# # ===============================
# CFG_PATH = r"D:\zra\PROJECTS\internship_astro\rehab-eercises\Rahabilities-General\config.json"
# LOG_PATH = r"D:\zra\PROJECTS\internship_astro\rehab-eercises\Rahabilities-General\logs"

# st.set_page_config(page_title="Rehab Monitor - Doctor UI", layout="wide")
# st.title("🏥 Rehab Monitor — Doctor Panel")

# if not os.path.exists(CFG_PATH):
#     st.error("❌ config.json not found. Please ensure it exists.")
#     st.stop()

# with open(CFG_PATH, "r", encoding="utf-8") as f:
#     cfg = json.load(f)

# # ===============================
# # HELPER FUNCTIONS
# # ===============================
# def get_default(section, key, default):
#     state_key = f"{section}_{key}"
#     if state_key in st.session_state:
#         return st.session_state[state_key]
#     value = cfg.get(section, {}).get(key, default)
#     st.session_state[state_key] = value
#     return value

# def save_cfg(section, **kwargs):
#     cfg[section] = kwargs
#     for k,v in kwargs.items():
#         st.session_state[f"{section}_{k}"] = v
#     with open(CFG_PATH, "w", encoding="utf-8") as f:
#         json.dump(cfg, f, indent=2)
#     st.success(f"✅ {section.replace('_',' ').title()} settings saved!")

# def two_col_inputs(label, key_min, key_max, min_val, max_val, step=1):
#     col1, col2 = st.columns(2)
#     with col1:
#         val_min = st.number_input(f"{label} Min", min_val, max_val, int(get_default(key_min[0], key_min[1], min_val)), step=step)
#     with col2:
#         val_max = st.number_input(f"{label} Max", min_val, max_val, int(get_default(key_max[0], key_max[1], max_val)), step=step)
#     return val_min, val_max
# # ===============================
# # SIDEBAR — SESSION CONTROL
# # ===============================
# exercise_name = st.sidebar.selectbox(
#     "Select Exercise",
#     ["shoulder_flexion","arm_raise_and_carry","mini_squat","wall_calf_stretch",
#      "straight_leg_raise","kettlebell_swings","seated_hip_internal_rotation",
#      "farmers_carry","bodyweight_deadlift","single_leg_stance","tandem_walk"]
# )

# st.sidebar.markdown("---")
# start_live = st.sidebar.button("▶ Start Live Session")
# stop_live = st.sidebar.button("⏹ Stop Session")
# st.session_state['stop_live'] = False

# # ===============================
# # EXERCISE PANELS WITH MIN/MAX RANGES
# # ===============================

# def shoulder_flexion_panel():
#     st.subheader("Shoulder Flexion Settings")
#     side = st.selectbox("Side", ["both","right","left"], index=["both","right","left"].index(get_default("shoulder_flexion","side","both")))
#     target_up_min = st.number_input("Target Angle UP Min", 0, 180, int(get_default("shoulder_flexion","target_angle_up_min",120)))
#     target_up_max = st.number_input("Target Angle UP Max", 0, 180, int(get_default("shoulder_flexion","target_angle_up_max",180)))
#     target_down_min = st.number_input("Target Angle DOWN Min", 0, 180, int(get_default("shoulder_flexion","target_angle_down_min",0)))
#     target_down_max = st.number_input("Target Angle DOWN Max", 0, 180, int(get_default("shoulder_flexion","target_angle_down_max",90)))
#     tol_min = st.number_input("Tolerance Min (deg)",0,30,int(get_default("shoulder_flexion","tolerance_min",5)))
#     tol_max = st.number_input("Tolerance Max (deg)",0,30,int(get_default("shoulder_flexion","tolerance_max",30)))
#     hold_min = st.number_input("Hold Time Min (sec)",0.1,10,float(get_default("shoulder_flexion","hold_time_min",0.5)))
#     hold_max = st.number_input("Hold Time Max (sec)",0.1,10,float(get_default("shoulder_flexion","hold_time_max",5.0)))
#     if st.button("💾 Save Shoulder Flexion"):
#         save_cfg("shoulder_flexion",
#                  side=side,
#                  target_angle_up_min=target_up_min, target_angle_up_max=target_up_max,
#                  target_angle_down_min=target_down_min, target_angle_down_max=target_down_max,
#                  tolerance_min=tol_min, tolerance_max=tol_max,
#                  hold_time_min=hold_min, hold_time_max=hold_max)

# def arm_raise_panel():
#     st.subheader("Arm Raise + Carry Settings")
#     side = st.selectbox("Side", ["both","right","left"], index=["both","right","left"].index(get_default("arm_raise_and_carry","side","both")))
#     target_up_min = st.number_input("Target Angle UP Min", 0, 180, int(get_default("arm_raise_and_carry","target_angle_up_min",120)))
#     target_up_max = st.number_input("Target Angle UP Max", 0, 180, int(get_default("arm_raise_and_carry","target_angle_up_max",180)))
#     target_down_min = st.number_input("Target Angle DOWN Min",0,180,int(get_default("arm_raise_and_carry","target_angle_down_min",0)))
#     target_down_max = st.number_input("Target Angle DOWN Max",0,180,int(get_default("arm_raise_and_carry","target_angle_down_max",90)))
#     hold_min = st.number_input("Hold Time Min (sec)",0.1,10,float(get_default("arm_raise_and_carry","hold_time_min",0.5)))
#     hold_max = st.number_input("Hold Time Max (sec)",0.1,10,float(get_default("arm_raise_and_carry","hold_time_max",5.0)))
#     carry_dur_min = st.number_input("Carry Duration Min (sec)",1,300,int(get_default("arm_raise_and_carry","carry_duration_min",5)))
#     carry_dur_max = st.number_input("Carry Duration Max (sec)",1,300,int(get_default("arm_raise_and_carry","carry_duration_max",120)))
#     carry_frac_min = st.number_input("Carry OK Fraction Min (%)",0,100,int(get_default("arm_raise_and_carry","carry_min_ok_fraction_min",50)))
#     carry_frac_max = st.number_input("Carry OK Fraction Max (%)",0,100,int(get_default("arm_raise_and_carry","carry_min_ok_fraction_max",100)))
#     if st.button("💾 Save Arm Raise + Carry"):
#         save_cfg("arm_raise_and_carry",
#                  side=side,
#                  target_angle_up_min=target_up_min, target_angle_up_max=target_up_max,
#                  target_angle_down_min=target_down_min, target_angle_down_max=target_down_max,
#                  hold_time_min=hold_min, hold_time_max=hold_max,
#                  carry_duration_min=carry_dur_min, carry_duration_max=carry_dur_max,
#                  carry_min_ok_fraction_min=carry_frac_min, carry_min_ok_fraction_max=carry_frac_max)

# def mini_squat_panel():
#     st.subheader("Mini Squat Settings")
#     side = st.selectbox("Side", ["both","left","right"], index=["both","left","right"].index(get_default("mini_squat","side","both")))
#     down_min = st.number_input("Down Knee Angle Min", 0, 180, int(get_default("mini_squat","down_knee_angle_min",40)))
#     down_max = st.number_input("Down Knee Angle Max", 0, 180, int(get_default("mini_squat","down_knee_angle_max",120)))
#     up_min = st.number_input("Up Knee Angle Min", 0, 180, int(get_default("mini_squat","up_knee_angle_min",120)))
#     up_max = st.number_input("Up Knee Angle Max", 0, 180, int(get_default("mini_squat","up_knee_angle_max",180)))
#     tilt_min = st.number_input("Max Torso Tilt Min",0,90,int(get_default("mini_squat","max_torso_tilt_min",0)))
#     tilt_max = st.number_input("Max Torso Tilt Max",0,90,int(get_default("mini_squat","max_torso_tilt_max",30)))
#     heel_min = st.number_input("Heel Lift Threshold Min",0,30,int(get_default("mini_squat","heel_lift_thresh_min",0)))
#     heel_max = st.number_input("Heel Lift Threshold Max",0,30,int(get_default("mini_squat","heel_lift_thresh_max",15)))
#     smooth_min = st.number_input("Smoothing Window Min",1,20,int(get_default("mini_squat","smoothing_window_min",1)))
#     smooth_max = st.number_input("Smoothing Window Max",1,20,int(get_default("mini_squat","smoothing_window_max",10)))
#     if st.button("💾 Save Mini Squat"):
#         save_cfg("mini_squat",
#                  side=side,
#                  down_knee_angle_min=down_min, down_knee_angle_max=down_max,
#                  up_knee_angle_min=up_min, up_knee_angle_max=up_max,
#                  max_torso_tilt_min=tilt_min, max_torso_tilt_max=tilt_max,
#                  heel_lift_thresh_min=heel_min, heel_lift_thresh_max=heel_max,
#                  smoothing_window_min=smooth_min, smoothing_window_max=smooth_max)

# def wall_calf_panel():
#     st.subheader("Wall Calf Stretch Settings")
#     side = st.selectbox("Side", ["both","left","right"], index=["both","left","right"].index(get_default("wall_calf_stretch","side","both")))
#     ankle_min = st.number_input("Ankle Stretch Min (deg)",0,180,int(get_default("wall_calf_stretch","ankle_stretch_min",150)))
#     ankle_max = st.number_input("Ankle Stretch Max (deg)",0,180,int(get_default("wall_calf_stretch","ankle_stretch_max",180)))
#     wrist_min = st.number_input("Wrist Stretch Min (deg)",0,180,int(get_default("wall_calf_stretch","wrist_stretch_min",120)))
#     wrist_max = st.number_input("Wrist Stretch Max (deg)",0,180,int(get_default("wall_calf_stretch","wrist_stretch_max",180)))
#     arm_min = st.number_input("Arm Straightness Min (deg)",0,180,int(get_default("wall_calf_stretch","arm_straight_min",120)))
#     arm_max = st.number_input("Arm Straightness Max (deg)",0,180,int(get_default("wall_calf_stretch","arm_straight_max",180)))
#     tol_min = st.number_input("Tolerance Min (deg)",0,30,int(get_default("wall_calf_stretch","tolerance_min",1)))
#     tol_max = st.number_input("Tolerance Max (deg)",0,30,int(get_default("wall_calf_stretch","tolerance_max",15)))
#     if st.button("💾 Save Wall Calf Stretch"):
#         save_cfg("wall_calf_stretch",
#                  side=side,
#                  ankle_stretch_min=ankle_min, ankle_stretch_max=ankle_max,
#                  wrist_stretch_min=wrist_min, wrist_stretch_max=wrist_max,
#                  arm_straight_min=arm_min, arm_straight_max=arm_max,
#                  tolerance_min=tol_min, tolerance_max=tol_max)

# def straight_leg_panel():
#     st.subheader("Straight Leg Raise Settings")
#     target_min = st.number_input("Target Angle Min (deg)",0,180,int(get_default("straight_leg_raise","target_min",30)))
#     target_max = st.number_input("Target Angle Max (deg)",0,180,int(get_default("straight_leg_raise","target_max",120)))
#     tol_min = st.number_input("Tolerance Min (deg)",0,30,int(get_default("straight_leg_raise","tolerance_min",5)))
#     tol_max = st.number_input("Tolerance Max (deg)",0,30,int(get_default("straight_leg_raise","tolerance_max",15)))
#     hold_min = st.number_input("Hold Time Min (sec)",0.1,10,float(get_default("straight_leg_raise","hold_time_min",0.5)))
#     hold_max = st.number_input("Hold Time Max (sec)",0.1,10,float(get_default("straight_leg_raise","hold_time_max",5.0)))
#     if st.button("💾 Save Straight Leg Raise"):
#         save_cfg("straight_leg_raise",
#                  target_min=target_min, target_max=target_max,
#                  tolerance_min=tol_min, tolerance_max=tol_max,
#                  hold_time_min=hold_min, hold_time_max=hold_max)

# # kettlebell_swings
# def kettlebell_panel():
#     st.subheader("Kettlebell Swings Settings")
#     swing_min = st.number_input("Swing Angle Min (deg)", 0, 180, int(get_default("kettlebell_swings","swing_min",60)))
#     swing_max = st.number_input("Swing Angle Max (deg)", 0, 180, int(get_default("kettlebell_swings","swing_max",180)))
#     tilt_min = st.number_input("Max Torso Tilt Min (deg)", 0, 90, int(get_default("kettlebell_swings","tilt_min",0)))
#     tilt_max = st.number_input("Max Torso Tilt Max (deg)", 0, 90, int(get_default("kettlebell_swings","tilt_max",40)))
#     tol_min = st.number_input("Rep Tolerance Min (deg)", 0, 30, int(get_default("kettlebell_swings","tol_min",1)))
#     tol_max = st.number_input("Rep Tolerance Max (deg)", 0, 30, int(get_default("kettlebell_swings","tol_max",15)))
#     if st.button("💾 Save Kettlebell Swings"):
#         save_cfg("kettlebell_swings",
#                  swing_min=swing_min, swing_max=swing_max,
#                  tilt_min=tilt_min, tilt_max=tilt_max,
#                  rep_tolerance_min=tol_min, rep_tolerance_max=tol_max)

# # seated_hip_internal_rotation
# def seated_hip_panel():
#     st.subheader("Seated Hip Internal Rotation Settings")
#     target_min = st.number_input("Target Rotation Min (deg)", 0, 180, int(get_default("seated_hip_internal_rotation","target_min",10)))
#     target_max = st.number_input("Target Rotation Max (deg)", 0, 180, int(get_default("seated_hip_internal_rotation","target_max",90)))
#     tol_min = st.number_input("Tolerance Min (deg)", 0, 30, int(get_default("seated_hip_internal_rotation","tolerance_min",1)))
#     tol_max = st.number_input("Tolerance Max (deg)", 0, 30, int(get_default("seated_hip_internal_rotation","tolerance_max",15)))
#     if st.button("💾 Save Seated Hip Internal Rotation"):
#         save_cfg("seated_hip_internal_rotation",
#                  target_min=target_min, target_max=target_max,
#                  tolerance_min=tol_min, tolerance_max=tol_max)

# # farmers_carry
# def farmers_carry_panel():
#     st.subheader("Farmer's Carry Settings")
#     dur_min = st.number_input("Carry Duration Min (sec)", 1, 300, int(get_default("farmers_carry","carry_duration_min",5)))
#     dur_max = st.number_input("Carry Duration Max (sec)", 1, 300, int(get_default("farmers_carry","carry_duration_max",120)))
#     frac_min = st.number_input("Min Success Fraction Min (%)", 0, 100, int(get_default("farmers_carry","carry_min_ok_fraction_min",50)))
#     frac_max = st.number_input("Min Success Fraction Max (%)", 0, 100, int(get_default("farmers_carry","carry_min_ok_fraction_max",100)))
#     if st.button("💾 Save Farmer's Carry"):
#         save_cfg("farmers_carry",
#                  carry_duration_min=dur_min, carry_duration_max=dur_max,
#                  carry_min_ok_fraction_min=frac_min, carry_min_ok_fraction_max=frac_max)

# # bodyweight_deadlift
# def bodyweight_deadlift_panel():
#     st.subheader("Bodyweight Deadlift Settings")
#     tilt_min = st.number_input("Max Torso Tilt Min (deg)", 0, 90, int(get_default("bodyweight_deadlift","tilt_min",0)))
#     tilt_max = st.number_input("Max Torso Tilt Max (deg)", 0, 90, int(get_default("bodyweight_deadlift","tilt_max",40)))
#     if st.button("💾 Save Bodyweight Deadlift"):
#         save_cfg("bodyweight_deadlift",
#                  max_torso_tilt_min=tilt_min, max_torso_tilt_max=tilt_max)

# # single_leg_stance
# def single_leg_panel():
#     st.subheader("Single Leg Stance Settings")
#     duration_min = st.number_input("Min Hold Duration Min (sec)", 0, 120, int(get_default("single_leg_stance","min_hold_min",5)))
#     duration_max = st.number_input("Min Hold Duration Max (sec)", 0, 120, int(get_default("single_leg_stance","min_hold_max",60)))
#     sway_min = st.number_input("Max Sway Min (deg)", 0, 30, int(get_default("single_leg_stance","max_sway_min",0)))
#     sway_max = st.number_input("Max Sway Max (deg)", 0, 30, int(get_default("single_leg_stance","max_sway_max",20)))
#     if st.button("💾 Save Single Leg Stance"):
#         save_cfg("single_leg_stance",
#                  min_hold_min=duration_min, min_hold_max=duration_max,
#                  max_sway_min=sway_min, max_sway_max=sway_max)

# # tandem_walk
# def tandem_walk_panel():
#     st.subheader("Tandem Walk Settings")
#     step_min = st.number_input("Step Length Min (cm)", 0, 200, int(get_default("tandem_walk","step_length_min",20)))
#     step_max = st.number_input("Step Length Max (cm)", 0, 200, int(get_default("tandem_walk","step_length_max",80)))
#     sway_min = st.number_input("Max Sway Min (deg)", 0, 30, int(get_default("tandem_walk","max_sway_min",0)))
#     sway_max = st.number_input("Max Sway Max (deg)", 0, 30, int(get_default("tandem_walk","max_sway_max",20)))
#     if st.button("💾 Save Tandem Walk"):
#         save_cfg("tandem_walk",
#                  step_length_min=step_min, step_length_max=step_max,
#                  max_sway_min=sway_min, max_sway_max=sway_max)

# # ===============================
# # Remaining exercises (kettlebell_swings, seated_hip, farmers_carry, bodyweight_deadlift, single_leg_stance, tandem_walk)
# # follow the same pattern: each criterion has min/max inputs
# # ===============================

# # For brevity, I will now update all remaining panels similarly:
# # kettlebell_panel
# def kettlebell_panel():
#     st.subheader("Kettlebell Swings Settings")
#     swing_min = st.number_input("Swing Angle Min (deg)",0,180,int(get_default("kettlebell_swings","swing_min",60)))
#     swing_max = st.number_input("Swing Angle Max (deg)",0,180,int(get_default("kettlebell_swings","swing_max",180)))
#     tilt_min = st.number_input("Max Torso Tilt Min (deg)",0,90,int(get_default("kettlebell_swings","tilt_min",0)))
#     tilt_max = st.number_input("Max Torso Tilt Max (deg)",0,90,int(get_default("kettlebell_swings","tilt_max",40)))
#     tol_min = st.number_input("Rep Tolerance Min (deg)",0,30,int(get_default("kettlebell_swings","tol_min",1)))
#     tol_max = st.number_input("Rep Tolerance Max (deg)",0,30,int(get_default("kettlebell_swings","tol_max",15)))
#     if st.button("💾 Save Kettlebell Swings"):
#         save_cfg("kettlebell_swings",
#                  swing_min=swing_min, swing_max=swing_max,
#                  tilt_min=tilt_min, tilt_max=tilt_max,
#                  rep_tolerance_min=tol_min, rep_tolerance_max=tol_max)

# # seated_hip_panel
# def seated_hip_panel():
#     st.subheader("Seated Hip Internal Rotation Settings")
#     target_min = st.number_input("Target Rotation Min (deg)",0,180,int(get_default("seated_hip_internal_rotation","target_min",10)))
#     target_max = st.number_input("Target Rotation Max (deg)",0,180,int(get_default("seated_hip_internal_rotation","target_max",90)))
#     tol_min = st.number_input("Tolerance Min (deg)",0,30,int(get_default("seated_hip_internal_rotation","tolerance_min",1)))
#     tol_max = st.number_input("Tolerance Max (deg)",0,30,int(get_default("seated_hip_internal_rotation","tolerance_max",15)))
#     if st.button("💾 Save Seated Hip Internal Rotation"):
#         save_cfg("seated_hip_internal_rotation",
#                  target_min=target_min, target_max=target_max,
#                  tolerance_min=tol_min, tolerance_max=tol_max)

# # farmers_carry_panel
# def farmers_carry_panel():
#     st.subheader("Farmer's Carry Settings")
#     dur_min = st.number_input("Carry Duration Min (sec)",1,300,int(get_default("farmers_carry","carry_duration_min",5)))
#     dur_max = st.number_input("Carry Duration Max (sec)",1,300,int(get_default("farmers_carry","carry_duration_max",120)))
#     frac_min = st.number_input("Min Success Fraction Min (%)",0,100,int(get_default("farmers_carry","carry_min_ok_fraction_min",50)))
#     frac_max = st.number_input("Min Success Fraction Max (%)",0,100,int(get_default("farmers_carry","carry_min_ok_fraction_max",100)))
#     if st.button("💾 Save Farmer's Carry"):
#         save_cfg("farmers_carry",
#                  carry_duration_min=dur_min, carry_duration_max=dur_max,
#                  carry_min_ok_fraction_min=frac_min, carry_min_ok_fraction_max=frac_max)

# # bodyweight_deadlift_panel
# def bodyweight_deadlift_panel():
#     st.subheader("Bodyweight Deadlift Settings")
#     tilt_min = st.number_input("Max Torso Tilt Min (deg)",0,90,int(get_default("bodyweight_deadlift","tilt_min",0)))
#     tilt_max = st.number_input("Max Torso Tilt Max (deg)",0,90,int(get_default("bodyweight_deadlift","tilt_max",40)))
#     if st.button("💾 Save Bodyweight Deadlift"):
#         save_cfg("bodyweight_deadlift",
#                  max_torso_tilt_min=tilt_min, max_torso_tilt_max=tilt_max)

# # single_leg_panel
# def single_leg_panel():
#     st.subheader("Single Leg Stance Settings")
#     duration_min = st.number_input("Min Hold Duration Min (sec)",0,120,int(get_default("single_leg_stance","min_hold_min",5)))
#     duration_max = st.number_input("Min Hold Duration Max (sec)",0,120,int(get_default("single_leg_stance","min_hold_max",60)))
#     sway_min = st.number_input("Max Sway Min (deg)",0,30,int(get_default("single_leg_stance","max_sway_min",0)))
#     sway_max = st.number_input("Max Sway Max (deg)",0,30,int(get_default("single_leg_stance","max_sway_max",20)))
#     if st.button("💾 Save Single Leg Stance"):
#         save_cfg("single_leg_stance",
#                  min_hold_min=duration_min, min_hold_max=duration_max,
#                  max_sway_min=sway_min, max_sway_max=sway_max)

# # tandem_walk_panel
# def tandem_walk_panel():
#     st.subheader("Tandem Walk Settings")
#     step_min = st.number_input("Step Length Min (cm)",0,200,int(get_default("tandem_walk","step_length_min",20)))
#     step_max = st.number_input("Step Length Max (cm)",0,200,int(get_default("tandem_walk","step_length_max",80)))
#     sway_min = st.number_input("Max Sway Min (deg)",0,30,int(get_default("tandem_walk","max_sway_min",0)))
#     sway_max = st.number_input("Max Sway Max (deg)",0,30,int(get_default("tandem_walk","max_sway_max",20)))
#     if st.button("💾 Save Tandem Walk"):
#         save_cfg("tandem_walk",
#                  step_length_min=step_min, step_length_max=step_max,
#                  max_sway_min=sway_min, max_sway_max=sway_max)

# # ===============================
# # PANEL MAPPING
# # ===============================
# exercise_panels = {
#     "shoulder_flexion": shoulder_flexion_panel,
#     "arm_raise_and_carry": arm_raise_panel,
#     "mini_squat": mini_squat_panel,
#     "wall_calf_stretch": wall_calf_panel,
#     "straight_leg_raise": straight_leg_panel,
#     "kettlebell_swings": kettlebell_panel,
#     "seated_hip_internal_rotation": seated_hip_panel,
#     "farmers_carry": farmers_carry_panel,
#     "bodyweight_deadlift": bodyweight_deadlift_panel,
#     "single_leg_stance": single_leg_panel,
#     "tandem_walk": tandem_walk_panel
# }

# if exercise_name in exercise_panels:
#     exercise_panels[exercise_name]()

# # ===============================
# # LIVE SESSION STREAM
# # ===============================
# if start_live:
#     st.session_state['stop_live'] = False
#     st.sidebar.success(f"Launching live session for '{exercise_name}'...")
#     frame_placeholder = st.empty()

#     for frame, res in run_exercise_live(exercise_name):
#         if st.session_state.get('stop_live'):
#             break
#         frame_placeholder.image(frame, channels="BGR")
#         if isinstance(res, dict):
#             if "reps" in res: st.write(f"Reps: {res['reps']}")
#             if "stage" in res: st.write(f"Stage: {res['stage']}")
#             if "feedback" in res: st.write("Feedback:", ", ".join(res["feedback"]))

# if stop_live:
#     st.session_state['stop_live'] = True
#     st.sidebar.warning("⏹ Live session stopped by doctor.")

# # ===============================
# # SESSION LOGS DISPLAY
# # ===============================
# st.markdown("---")
# st.header("📊 Session Logs")
# if os.path.exists(LOG_PATH):
#     all_csvs = [f for f in os.listdir(LOG_PATH) if f.endswith(".csv")]
#     for f in all_csvs:
#         st.markdown(f"**{f}**")
#         df = pd.read_csv(os.path.join(LOG_PATH,f), on_bad_lines='skip')
#         st.dataframe(df.tail(100))
#         st.download_button(f"⬇️ Download {f}", data=df.to_csv(index=False), file_name=f)
# else:
#     st.info("Logs folder not found.")
import streamlit as st
import json, os
import pandas as pd
from run_local import run_exercise_live

# ===============================
# CONFIG & PATHS
# ===============================
CFG_PATH = r"D:\zra\PROJECTS\internship_astro\rehab-eercises\Rahabilities-General\config.json"
LOG_PATH = r"D:\zra\PROJECTS\internship_astro\rehab-eercises\Rahabilities-General\logs"

st.set_page_config(page_title="Rehab Monitor - Doctor UI", layout="wide")
st.title("🏥 Rehab Monitor — Doctor Panel")

if not os.path.exists(CFG_PATH):
    st.error("❌ config.json not found. Please ensure it exists.")
    st.stop()

with open(CFG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)

# ===============================
# HELPER FUNCTIONS
# ===============================
def get_default(section, key, default):
    state_key = f"{section}_{key}"
    if state_key in st.session_state:
        return st.session_state[state_key]
    value = cfg.get(section, {}).get(key, default)
    st.session_state[state_key] = value
    return value

def save_cfg(section, **kwargs):
    cfg[section] = kwargs
    for k, v in kwargs.items():
        st.session_state[f"{section}_{k}"] = v
    with open(CFG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    st.success(f"✅ {section.replace('_',' ').title()} settings saved!")

def two_col_inputs(label, key_min, key_max, min_val, max_val, step=1):
    col1, col2 = st.columns(2)
    with col1:
        val_min = st.number_input(
            f"{label} Min", min_val, max_val, int(get_default(key_min[0], key_min[1], min_val)), step=step
        )
    with col2:
        val_max = st.number_input(
            f"{label} Max", min_val, max_val, int(get_default(key_max[0], key_max[1], max_val)), step=step
        )
    return val_min, val_max

# ===============================
# EXERCISE PANELS
# ===============================

def shoulder_flexion_panel():
    st.subheader("Shoulder Flexion Settings")
    side = st.selectbox("Side", ["both","right","left"], index=["both","right","left"].index(get_default("shoulder_flexion","side","both")))
    target_up_min, target_up_max = two_col_inputs("Target Angle UP", ("shoulder_flexion","target_angle_up_min"), ("shoulder_flexion","target_angle_up_max"), 0, 180)
    target_down_min, target_down_max = two_col_inputs("Target Angle DOWN", ("shoulder_flexion","target_angle_down_min"), ("shoulder_flexion","target_angle_down_max"), 0, 180)
    tol_min, tol_max = two_col_inputs("Tolerance (deg)", ("shoulder_flexion","tolerance_min"), ("shoulder_flexion","tolerance_max"), 0, 30)
    hold_min, hold_max = two_col_inputs("Hold Time (sec)", ("shoulder_flexion","hold_time_min"), ("shoulder_flexion","hold_time_max"), 0.1, 10, step=0.1)
    if st.button("💾 Save Shoulder Flexion"):
        save_cfg("shoulder_flexion",
                 side=side,
                 target_angle_up_min=target_up_min, target_angle_up_max=target_up_max,
                 target_angle_down_min=target_down_min, target_angle_down_max=target_down_max,
                 tolerance_min=tol_min, tolerance_max=tol_max,
                 hold_time_min=hold_min, hold_time_max=hold_max)

def arm_raise_panel():
    st.subheader("Arm Raise + Carry Settings")
    side = st.selectbox("Side", ["both","right","left"], index=["both","right","left"].index(get_default("arm_raise_and_carry","side","both")))
    target_up_min, target_up_max = two_col_inputs("Target Angle UP", ("arm_raise_and_carry","target_angle_up_min"), ("arm_raise_and_carry","target_angle_up_max"), 0, 180)
    target_down_min, target_down_max = two_col_inputs("Target Angle DOWN", ("arm_raise_and_carry","target_angle_down_min"), ("arm_raise_and_carry","target_angle_down_max"), 0, 180)
    hold_min, hold_max = two_col_inputs("Hold Time (sec)", ("arm_raise_and_carry","hold_time_min"), ("arm_raise_and_carry","hold_time_max"), 0.1, 10, step=0.1)
    carry_dur_min, carry_dur_max = two_col_inputs("Carry Duration (sec)", ("arm_raise_and_carry","carry_duration_min"), ("arm_raise_and_carry","carry_duration_max"), 1, 300)
    carry_frac_min, carry_frac_max = two_col_inputs("Carry OK Fraction (%)", ("arm_raise_and_carry","carry_min_ok_fraction_min"), ("arm_raise_and_carry","carry_min_ok_fraction_max"), 0, 100)
    if st.button("💾 Save Arm Raise + Carry"):
        save_cfg("arm_raise_and_carry",
                 side=side,
                 target_angle_up_min=target_up_min, target_angle_up_max=target_up_max,
                 target_angle_down_min=target_down_min, target_angle_down_max=target_down_max,
                 hold_time_min=hold_min, hold_time_max=hold_max,
                 carry_duration_min=carry_dur_min, carry_duration_max=carry_dur_max,
                 carry_min_ok_fraction_min=carry_frac_min, carry_min_ok_fraction_max=carry_frac_max)

# Repeat the same two-column min/max style for all other exercises
def mini_squat_panel():
    st.subheader("Mini Squat Settings")
    side = st.selectbox("Side", ["both","left","right"], index=["both","left","right"].index(get_default("mini_squat","side","both")))
    down_min, down_max = two_col_inputs("Down Knee Angle", ("mini_squat","down_knee_angle_min"), ("mini_squat","down_knee_angle_max"), 0, 180)
    up_min, up_max = two_col_inputs("Up Knee Angle", ("mini_squat","up_knee_angle_min"), ("mini_squat","up_knee_angle_max"), 0, 180)
    tilt_min, tilt_max = two_col_inputs("Max Torso Tilt", ("mini_squat","max_torso_tilt_min"), ("mini_squat","max_torso_tilt_max"), 0, 90)
    heel_min, heel_max = two_col_inputs("Heel Lift Threshold", ("mini_squat","heel_lift_thresh_min"), ("mini_squat","heel_lift_thresh_max"), 0, 30)
    smooth_min, smooth_max = two_col_inputs("Smoothing Window", ("mini_squat","smoothing_window_min"), ("mini_squat","smoothing_window_max"), 1, 20)
    if st.button("💾 Save Mini Squat"):
        save_cfg("mini_squat",
                 side=side,
                 down_knee_angle_min=down_min, down_knee_angle_max=down_max,
                 up_knee_angle_min=up_min, up_knee_angle_max=up_max,
                 max_torso_tilt_min=tilt_min, max_torso_tilt_max=tilt_max,
                 heel_lift_thresh_min=heel_min, heel_lift_thresh_max=heel_max,
                 smoothing_window_min=smooth_min, smoothing_window_max=smooth_max)

def wall_calf_panel():
    st.subheader("Wall Calf Stretch Settings")
    side = st.selectbox("Side", ["both","left","right"], index=["both","left","right"].index(get_default("wall_calf_stretch","side","both")))
    ankle_min, ankle_max = two_col_inputs("Ankle Stretch (deg)", ("wall_calf_stretch","ankle_stretch_min"), ("wall_calf_stretch","ankle_stretch_max"), 0, 180)
    wrist_min, wrist_max = two_col_inputs("Wrist Stretch (deg)", ("wall_calf_stretch","wrist_stretch_min"), ("wall_calf_stretch","wrist_stretch_max"), 0, 180)
    arm_min, arm_max = two_col_inputs("Arm Straightness (deg)", ("wall_calf_stretch","arm_straight_min"), ("wall_calf_stretch","arm_straight_max"), 0, 180)
    tol_min, tol_max = two_col_inputs("Tolerance (deg)", ("wall_calf_stretch","tolerance_min"), ("wall_calf_stretch","tolerance_max"), 0, 30)
    if st.button("💾 Save Wall Calf Stretch"):
        save_cfg("wall_calf_stretch",
                 side=side,
                 ankle_stretch_min=ankle_min, ankle_stretch_max=ankle_max,
                 wrist_stretch_min=wrist_min, wrist_stretch_max=wrist_max,
                 arm_straight_min=arm_min, arm_straight_max=arm_max,
                 tolerance_min=tol_min, tolerance_max=tol_max)
def straight_leg_panel():
    st.subheader("Straight Leg Raise Settings")
    target_min = st.number_input("Target Angle Min (deg)",0,180,int(get_default("straight_leg_raise","target_min",30)))
    target_max = st.number_input("Target Angle Max (deg)",0,180,int(get_default("straight_leg_raise","target_max",120)))
    tol_min = st.number_input("Tolerance Min (deg)",0,30,int(get_default("straight_leg_raise","tolerance_min",5)))
    tol_max = st.number_input("Tolerance Max (deg)",0,30,int(get_default("straight_leg_raise","tolerance_max",15)))
    hold_min = st.number_input("Hold Time Min (sec)",0.1,10,float(get_default("straight_leg_raise","hold_time_min",0.5)))
    hold_max = st.number_input("Hold Time Max (sec)",0.1,10,float(get_default("straight_leg_raise","hold_time_max",5.0)))
    if st.button("💾 Save Straight Leg Raise"):
        save_cfg("straight_leg_raise",
                 target_min=target_min, target_max=target_max,
                 tolerance_min=tol_min, tolerance_max=tol_max,
                 hold_time_min=hold_min, hold_time_max=hold_max)

# kettlebell_swings
def kettlebell_panel():
    st.subheader("Kettlebell Swings Settings")
    swing_min = st.number_input("Swing Angle Min (deg)", 0, 180, int(get_default("kettlebell_swings","swing_min",60)))
    swing_max = st.number_input("Swing Angle Max (deg)", 0, 180, int(get_default("kettlebell_swings","swing_max",180)))
    tilt_min = st.number_input("Max Torso Tilt Min (deg)", 0, 90, int(get_default("kettlebell_swings","tilt_min",0)))
    tilt_max = st.number_input("Max Torso Tilt Max (deg)", 0, 90, int(get_default("kettlebell_swings","tilt_max",40)))
    tol_min = st.number_input("Rep Tolerance Min (deg)", 0, 30, int(get_default("kettlebell_swings","tol_min",1)))
    tol_max = st.number_input("Rep Tolerance Max (deg)", 0, 30, int(get_default("kettlebell_swings","tol_max",15)))
    if st.button("💾 Save Kettlebell Swings"):
        save_cfg("kettlebell_swings",
                 swing_min=swing_min, swing_max=swing_max,
                 tilt_min=tilt_min, tilt_max=tilt_max,
                 rep_tolerance_min=tol_min, rep_tolerance_max=tol_max)

# seated_hip_internal_rotation
def seated_hip_panel():
    st.subheader("Seated Hip Internal Rotation Settings")
    target_min = st.number_input("Target Rotation Min (deg)", 0, 180, int(get_default("seated_hip_internal_rotation","target_min",10)))
    target_max = st.number_input("Target Rotation Max (deg)", 0, 180, int(get_default("seated_hip_internal_rotation","target_max",90)))
    tol_min = st.number_input("Tolerance Min (deg)", 0, 30, int(get_default("seated_hip_internal_rotation","tolerance_min",1)))
    tol_max = st.number_input("Tolerance Max (deg)", 0, 30, int(get_default("seated_hip_internal_rotation","tolerance_max",15)))
    if st.button("💾 Save Seated Hip Internal Rotation"):
        save_cfg("seated_hip_internal_rotation",
                 target_min=target_min, target_max=target_max,
                 tolerance_min=tol_min, tolerance_max=tol_max)

# farmers_carry
def farmers_carry_panel():
    st.subheader("Farmer's Carry Settings")
    dur_min = st.number_input("Carry Duration Min (sec)", 1, 300, int(get_default("farmers_carry","carry_duration_min",5)))
    dur_max = st.number_input("Carry Duration Max (sec)", 1, 300, int(get_default("farmers_carry","carry_duration_max",120)))
    frac_min = st.number_input("Min Success Fraction Min (%)", 0, 100, int(get_default("farmers_carry","carry_min_ok_fraction_min",50)))
    frac_max = st.number_input("Min Success Fraction Max (%)", 0, 100, int(get_default("farmers_carry","carry_min_ok_fraction_max",100)))
    if st.button("💾 Save Farmer's Carry"):
        save_cfg("farmers_carry",
                 carry_duration_min=dur_min, carry_duration_max=dur_max,
                 carry_min_ok_fraction_min=frac_min, carry_min_ok_fraction_max=frac_max)

# bodyweight_deadlift
def bodyweight_deadlift_panel():
    st.subheader("Bodyweight Deadlift Settings")
    tilt_min = st.number_input("Max Torso Tilt Min (deg)", 0, 90, int(get_default("bodyweight_deadlift","tilt_min",0)))
    tilt_max = st.number_input("Max Torso Tilt Max (deg)", 0, 90, int(get_default("bodyweight_deadlift","tilt_max",40)))
    if st.button("💾 Save Bodyweight Deadlift"):
        save_cfg("bodyweight_deadlift",
                 max_torso_tilt_min=tilt_min, max_torso_tilt_max=tilt_max)

# single_leg_stance
def single_leg_panel():
    st.subheader("Single Leg Stance Settings")
    duration_min = st.number_input("Min Hold Duration Min (sec)", 0, 120, int(get_default("single_leg_stance","min_hold_min",5)))
    duration_max = st.number_input("Min Hold Duration Max (sec)", 0, 120, int(get_default("single_leg_stance","min_hold_max",60)))
    sway_min = st.number_input("Max Sway Min (deg)", 0, 30, int(get_default("single_leg_stance","max_sway_min",0)))
    sway_max = st.number_input("Max Sway Max (deg)", 0, 30, int(get_default("single_leg_stance","max_sway_max",20)))
    if st.button("💾 Save Single Leg Stance"):
        save_cfg("single_leg_stance",
                 min_hold_min=duration_min, min_hold_max=duration_max,
                 max_sway_min=sway_min, max_sway_max=sway_max)

# tandem_walk
def tandem_walk_panel():
    st.subheader("Tandem Walk Settings")
    step_min = st.number_input("Step Length Min (cm)", 0, 200, int(get_default("tandem_walk","step_length_min",20)))
    step_max = st.number_input("Step Length Max (cm)", 0, 200, int(get_default("tandem_walk","step_length_max",80)))
    sway_min = st.number_input("Max Sway Min (deg)", 0, 30, int(get_default("tandem_walk","max_sway_min",0)))
    sway_max = st.number_input("Max Sway Max (deg)", 0, 30, int(get_default("tandem_walk","max_sway_max",20)))
    if st.button("💾 Save Tandem Walk"):
        save_cfg("tandem_walk",
                 step_length_min=step_min, step_length_max=step_max,
                 max_sway_min=sway_min, max_sway_max=sway_max)
# PANEL MAPPING
# ===============================
exercise_panels = {
    "shoulder_flexion": shoulder_flexion_panel,
    "arm_raise_and_carry": arm_raise_panel,
    "mini_squat": mini_squat_panel,
    "wall_calf_stretch": wall_calf_panel,
    "straight_leg_raise": straight_leg_panel,
    "kettlebell_swings": kettlebell_panel,
    "seated_hip_internal_rotation": seated_hip_panel,
    "farmers_carry": farmers_carry_panel,
    "bodyweight_deadlift": bodyweight_deadlift_panel,
    "single_leg_stance": single_leg_panel,
    "tandem_walk": tandem_walk_panel
}

# -------------------------
# SIDEBAR — SELECT EXERCISE
# -------------------------
exercise_name = st.sidebar.selectbox(
    "Select Exercise",
    list(exercise_panels.keys())
)

st.sidebar.markdown("---")
start_live = st.sidebar.button("▶ Start Live Session")
stop_live = st.sidebar.button("⏹ Stop Session")
st.session_state['stop_live'] = False

# ===============================
# DISPLAY PANELS IN TWO COLUMNS
# ===============================
col_left, col_right = st.columns(2)

with col_left:
    if exercise_name in ["shoulder_flexion","arm_raise_and_carry","mini_squat","wall_calf_stretch"]:
        exercise_panels[exercise_name]()

with col_right:
    if exercise_name not in ["shoulder_flexion","arm_raise_and_carry","mini_squat","wall_calf_stretch"]:
        exercise_panels[exercise_name]()

# ===============================
# LIVE SESSION STREAM
# ===============================
if start_live:
    st.session_state['stop_live'] = False
    st.sidebar.success(f"Launching live session for '{exercise_name}'...")
    frame_placeholder = st.empty()

    for frame, res in run_exercise_live(exercise_name):
        if st.session_state.get('stop_live'):
            break
        frame_placeholder.image(frame, channels="BGR")
        if isinstance(res, dict):
            if "reps" in res: st.write(f"Reps: {res['reps']}")
            if "stage" in res: st.write(f"Stage: {res['stage']}")
            if "feedback" in res: st.write("Feedback:", ", ".join(res["feedback"]))

if stop_live:
    st.session_state['stop_live'] = True
    st.sidebar.warning("⏹ Live session stopped by doctor.")

# ===============================
# SESSION LOGS DISPLAY
# ===============================
st.markdown("---")
st.header("📊 Session Logs")
if os.path.exists(LOG_PATH):
    all_csvs = [f for f in os.listdir(LOG_PATH) if f.endswith(".csv")]
    for f in all_csvs:
        st.markdown(f"**{f}**")
        df = pd.read_csv(os.path.join(LOG_PATH,f), on_bad_lines='skip')
        st.dataframe(df.tail(100))
        st.download_button(f"⬇️ Download {f}", data=df.to_csv(index=False), file_name=f)
else:
    st.info("Logs folder not found.")