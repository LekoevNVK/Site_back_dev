# File Storage FastAPI

1. Create virtualenv & run:

    ```
    $ pip install -r requirements.txt
    ```

2. Run service with command:
    ```
    $ uvicorn app:app --reload
    ```

3. To run tests, execute in terminal:
    ```
    $ cd tests
    $ pytest
    ```

4. For Pip - Fatal error in launcher: Unable to create process using:
    ```
    $ python -m pip install --upgrade --force-reinstall pip
    ```
5. Fast API Swagger UI:
    ```
    http://127.0.0.1:8000/docs
    http://127.0.0.1:8000/api/get
    ```