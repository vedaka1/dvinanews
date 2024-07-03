## Project features
* Get latest news from dvinanews.ru
* Clean Architecture
* Functionality for admins
* Users can request admin rights
* Subscription to newsletter
## How to run
Set environment variables .env
```python
BOT_TOKEN=

POSTGRES_HOST=s 
POSTGRES_PORT=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

HEAD_ADMIN_TG_ID=
```
### Dev
* Run `docker compose up -d` or `make app` in the project directory
### Production
* Run Run `docker compose -f docker-compose.production.yml up -d` or `make prod` in the project directory

## Commands
* **/start** - Start interacting with the bot
* **/info** - Informations for admins
* **/request_access** - Request admin rights
* **/news** - Get latest news
* **/newsletter** - Subscribe to newsletter
* **/promote_user \<user id\>** - Promote user
* **/demote_user \<user id\>** - Demote user
* **/admins** - List of admins