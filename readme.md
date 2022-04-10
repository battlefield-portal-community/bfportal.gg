# Source code of bfportal.gg [WIP]
## How to run locally  
<details>
  
  <summary>
    Click to show !!!
  </summary>

- create and activate a venv
- install dependencies `python -m pip install -r requirements.txt`
- create a .env file with the following values
- ``` 
      DB_NAME=<postgres_db_name>
      DB_USERNAME=<postgres_username>
      DB_PASSWORD=<postgres_password>
      POSTGRES_HOST=127.0.0.1
      SU_PASSWD=1234
      DISCORD_CLIENT_ID=931965340764737608
      DISCORD_SECRET=SuzQK6oAV_ArY3HGXUYIOUjFT46C5OtW
    ```
- Do first run migrate
- run `python manage.py ensure_superuser --username bfportal --email superuser@bfportal.com --password <password>`
- run `python manage.py ensure_initialization`
- run server with `python manage.py runserver`
- login via discord to create a new user 
- run command `python manage.py fake --generate 50` to create a few fake pages
- reload admin now u should and a data to explore

</details>


### Screenshots of several parts of the website
<details>
  
  <summary>
    Click to show
  </summary>
 
![image](https://user-images.githubusercontent.com/22869882/162639043-ec231408-b2e2-4f7a-b89e-38e48fec75e3.png)
![image](https://user-images.githubusercontent.com/22869882/162639063-19c9bd0b-888b-4116-ab25-cfc3d67692ec.png)
![image](https://user-images.githubusercontent.com/22869882/162639079-105111d8-0557-4ce2-a697-6cb3b8091b16.png)
![image](https://user-images.githubusercontent.com/22869882/162639108-f3fef6b3-1c44-4283-a504-8ab959815bd8.png)
![image](https://user-images.githubusercontent.com/22869882/162639135-30265c6e-690a-47b2-b9c5-842f98061051.png)
![image](https://user-images.githubusercontent.com/22869882/162639149-6ca41096-9892-4c5c-ab3f-0d1c7dd9b1d0.png)

</details>
