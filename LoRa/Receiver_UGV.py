import serial
import time
import sys
import subprocess # For External Python scripts
import sx126x     # LoRa module library

# === SETTINGS ===
# Serial port of the LoRa module connected to the Raspberry Pi.
PORT = '/dev/ttyAMA0'  
BAUDRATE = 9600        # UART speed
#  Full path of the Python script to be executed
SCRIPT_TO_RUN_PATH = "UGV_codes/ugv_commands_code.py" 
# The command sequence expected from the computer.
EXPECTED_COMMAND = "RUN_UGV_COMMANDS_CODE_PY"
#  The file where the incoming data will be saved.
FILE_NAME = "UGV_codes/received_data.txt" 
# The time (in seconds) after which the program will close if no data is received.
TIMEOUT_SECONDS = 70 

def run_python_script(script_path, node_instance, sender_addr):
    """
    It executes the specified Python script and sends its output back via LoRa.
    """
    print(f"Script '{script_path}' is being executed...")
    response_message = ""
    try:
        result = subprocess.run(
            ["python3", script_path], 
            check=True, 
            capture_output=True, 
            text=True,
            timeout=30 # Maximum time for the script to run (in seconds)
        )
        print(f"Script completed successfully. Output:\n{result.stdout}")
        response_message = f"OK: '{script_path}' was executed successfully."
    except subprocess.CalledProcessError as e:
        print(f"Script execution error: {e.stderr}")
        response_message = f"ERROR: Error running '{script_path}': {e.stderr[:100]}" # Send the first 100 characters.
    except FileNotFoundError:
        print(f"Error: '{script_path}' not found. Check the directory.")
        response_message = f"ERROR: Script '{script_path}' not found."
    except subprocess.TimeoutExpired:
        print(f"Error: '{script_path}' timed out.")
        response_message = f"ERROR: '{script_path}' timed out."
    except Exception as e:
        print(f"Unexpected error: {e}")
        response_message = f"ERROR: An unexpected problem occurred: {str(e)[:100]}" # Send the first 100 characters.
    
    # Send your answer via LoRa.
    try:
        if sender_addr is not None:
            print(f"Sending reply: '{response_message}' -> Address: {sender_addr}")
            node_instance.send(sender_addr, response_message.encode('utf-8'))
        else:
            print("Reply could not be sent: Sender address unknown.")
    except Exception as e:
        print(f"LoRa reply sending error: {e}")

    return response_message 

try:
    # Initialize the sx126x node object.
    node = sx126x.sx126x(serial_num=PORT, freq=868, addr=0, power=22, rssi=True, air_speed=2400, relay=False)

    print(f"Listening... Port: {PORT}, Baudrate: {BAUDRATE}")
    print(f"The program will close if no data is received for {TIMEOUT_SECONDS} seconds (for LoRa data streams only).")
    print("Waiting for data... (Press Ctrl+C to exit)")

    # Open the file in write mode
    with open(FILE_NAME, "w", encoding='utf-8') as file:
        last_data_receive_time = time.time()

        while True:
            # Call the `receive` method of the LoRa library.
            received_packet = node.receive() 

            if received_packet:                 
                sender_addr = received_packet.get("sender_addr")
                target_addr = received_packet.get("target_addr")
                message = received_packet.get("message")
                rssi = received_packet.get("rssi")

                print(f"\n  Destination Address: {target_addr}")
                print(f"  Sender Address: {sender_addr}")
                print(f"  Message: {message}")
                if rssi is not None:
                    print(f"  RSSI: -{rssi}dBm")
                
                # Check incoming message
                if message == EXPECTED_COMMAND:
                    print(f"The awaited command was received: '{EXPECTED_COMMAND}'")
                    # Run the script and send the response back to the sender
                    run_python_script(SCRIPT_TO_RUN_PATH, node, sender_addr)
                else:
                    print(f"Unknown command or data: '{message}'")
                    # Save the incoming data to a file.
                    output_line = f"{message}"
                    file.write(output_line + '\n')
                    file.flush()

                last_data_receive_time = time.time() # Update the time when the data arrives.
                
            # Timeout control
            elif (time.time() - last_data_receive_time) > TIMEOUT_SECONDS:
                print(f"No data was received for {TIMEOUT_SECONDS} seconds. The program is closing.")
                break

            time.sleep(0.01) 

except serial.SerialException as e:
    print("🔌 Serial port error:", e)
    print("Please ensure the serial port is correct and not being used by another program.")
    print(f"Ensure the port matches the sending port: '{PORT}'.")
    print("You can check the port using the command 'ls /dev/tty*'.")

except KeyboardInterrupt:
    print("\n🛑 The program was stopped by the user (Ctrl+C).")

except Exception as e:
    print(f"❗ An unexpected error occurred: {e} ")
    import traceback
    traceback.print_exc(file=sys.stdout)

finally:
    # if 'node' in locals():
    #     node.close()
    print("Program sonlandırıldı.")