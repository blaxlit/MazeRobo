# main.py
import sys
import os
import time
from robomaster import robot

# Add path for import module in src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.config_loader import load_config
from src.chassis import ChassisController
from src.PID import PIDController

def drive_with_pid(target_x, target_y, pid_x, pid_y, chassis_ctrl, timeout=2.4, tolerance=0.08):
    """
    เพิ่ม timeout เป็น 8.0 วินาที เพื่อให้มีเวลาวิ่งถึงเป้าหมายได้ทัน
    เพิ่ม tolerance เป็น 0.08 (8 เซนติเมตร) ป้องกันหุ่นยนต์เดินเอื่อยๆ ช้าๆ ตอนใกล้ถึงเป้า
    """
    pid_x.reset()
    pid_y.reset()
    start_time = time.time()
    prev_time = start_time
    
    while (time.time() - start_time) < timeout:
        current_x = chassis_ctrl.x
        current_y = chassis_ctrl.y
        
        now = time.time()
        dt = now - prev_time
        prev_time = now
        if dt <= 0:
            dt = 0.01
            
        dist_error = ((target_x - current_x)**2 + (target_y - current_y)**2) ** 0.5
        
        if dist_error < tolerance:
            break
            
        vx_cmd = pid_x.compute(setpoint=target_x, measurement=current_x, dt=dt)
        vy_cmd = pid_y.compute(setpoint=target_y, measurement=current_y, dt=dt)
        
        chassis_ctrl.ep_chassis.drive_speed(x=vx_cmd, y=vy_cmd, z=0)
        time.sleep(0.05)
        
    chassis_ctrl.ep_chassis.drive_speed(x=0, y=0, z=0)

def main():
    config = load_config("config/settings.yaml")
    ep_robot = robot.Robot()
    
    pid_x = PIDController(kp=1.2, ki=0.0, kd=0.2, min_output=-0.5, max_output=0.5)
    pid_y = PIDController(kp=1.2, ki=0.0, kd=0.2, min_output=-0.5, max_output=0.5)
    
    try:
        print("Connecting robot ....")
        ep_robot.initialize()
        
        chassis_ctrl = ChassisController(ep_robot, config)
        
        chassis_ctrl.setup_csv_headers()
        chassis_ctrl.start_sensors()
        
        time.sleep(3) 

        # แกน X บวกลบคือน้ำหน้า/ถอยหลัง[cite: 7]
        # แกน Y บวกคือซ้าย ลบคือขวา[cite: 7]

        print("Leg 1: Driving Forward")
        # ไปข้างหน้า 1.2 เมตร (X=1.2, Y=0.0)
        drive_with_pid(target_x=0.5, target_y=0.0, pid_x=pid_x, pid_y=pid_y, chassis_ctrl=chassis_ctrl)
        time.sleep(3) 
        
        print("Leg 2: Strafing Right")
        # สไลด์ขวา ต้องเปลี่ยน Y เป็นค่าติดลบ (X=1.2, Y=-1.2)
        drive_with_pid(target_x=0, target_y=0.5, pid_x=pid_x, pid_y=pid_y, chassis_ctrl=chassis_ctrl)
        time.sleep(3)
        
        print("Leg 3: Driving Backward")
        # ถอยหลัง X กลับมาที่ 0.0 ส่วน Y ค้างไว้ที่เดิมทางขวา (X=0.0, Y=-1.2)
        drive_with_pid(target_x=-0.5, target_y=0.0, pid_x=pid_x, pid_y=pid_y, chassis_ctrl=chassis_ctrl)
        time.sleep(3)
        
        print("Leg 4: Strafing Left (Back to origin)")
        # สไลด์ซ้าย กลับมาจุดเริ่มต้นทั้ง X และ Y (X=0.0, Y=0.0)
        drive_with_pid(target_x=0.0, target_y=-0.5, pid_x=pid_x, pid_y=pid_y, chassis_ctrl=chassis_ctrl)
        
        time.sleep(3)
        
        chassis_ctrl.stop_sensors()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        chassis_ctrl.ep_chassis.drive_speed(x=0, y=0, z=0)
        ep_robot.close()
        print("Robot connection closed successfully.")

if __name__ == '__main__':
    main()