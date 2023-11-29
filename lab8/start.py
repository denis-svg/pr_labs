import threading
import subprocess

# Create a lock for synchronization
print_lock = threading.Lock()

def run_script(script_name):
    try:
        result = subprocess.run(f'python {script_name}', shell=True, check=True, capture_output=True, text=True)
        with print_lock:
            print(f"Output from {script_name}:")
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        with print_lock:
            print(f"Error executing {script_name}: {e}")
            print(f"Output from {script_name}:")
            print(e.output)

if __name__ == "__main__":
    # List of script names to run
    scripts = ['main.py 8000 1', 'main.py 8001 2', 'main.py 8002 3', 'main.py 8003 4']

    # Create and start a thread for each script
    threads = []
    for script in scripts:
        thread = threading.Thread(target=run_script, args=(script,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    print("All threads have finished.")
    scripts = ['app.py db1 saved_object1.pkl', 'app.py db2 saved_object2.pkl',
               'app.py db3 saved_object3.pkl', 'app.py db4 saved_object4.pkl']
    
    # Create and start a thread for each script
    threads = []
    for script in scripts:
        thread = threading.Thread(target=run_script, args=(script,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
