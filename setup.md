# Setup enviroment installation on Ubuntu 22.04

**1. Install Python 3.10:**

* **Check Existing Versions:**
    ```bash
    python3 --version
    ```
    If it's 3.10 or higher, skip to step 2.
* **Install Using `deadsnakes` PPA:**
    ```bash
    sudo add-apt-repository ppa:deadsnakes/ppa 
    sudo apt update
    sudo apt install python3.10
    ```

**2. Create a Virtual Environment:**

* **Install `venv`:** (if you haven't already)
    ```bash
    sudo apt install python3.10-venv
    ```
* **Navigate to your project directory:**
    ```bash
    cd your_project_directory
    ```
* **Create the environment:**
    ```bash
    python3.10 -m venv .venv 
    ```

**3. Activate the Environment:**

```bash
source .venv/bin/activate
```

**4. Install Dependencies:**

* **Make sure you have `pip`:**
    ```bash
    pip --version
    ```
    If it's not installed, run `sudo apt install python3-pip`
* **Install from `requirements.txt`:**
    ```bash
    pip install -r requirements.txt
    ```

**Explanation:**

* **Virtual Environments:** These isolate your project's dependencies from other Python projects, preventing conflicts.
* **`deadsnakes` PPA:** Provides newer Python versions than the default Ubuntu repositories.
* **`requirements.txt`:** Lists the packages your project needs, making it easy to share and recreate the environment.

**Important Notes:**

* **Replace `your_project_directory` and `.venv`** with your actual directory and environment names.
* **WSL Specifics:** These steps should work seamlessly in Ubuntu WSL.
* **Python 3.10 Availability:** Ensure Python 3.10 is available in the `deadsnakes` PPA for your Ubuntu version.

Let me know if you have any specific questions or need help with any errors you encounter! 
