## Project 3: Item Catalog

#### Project Overview
An application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

#### How to run the app
###### Vagrant

Install vagrant from [here](https://www.vagrantup.com/downloads.html)

* Use preconfigured Vagrant VMs to run the app.
* To use the Vagrant virtual machine, navigate to the fullstack-nanodegree-item-catalog/vagrant directory in the terminal, then use the command vagrant up (powers on the virtual machine) followed by vagrant ssh (logs into the virtual machine).
* After logging into VM (by vagrant ssh), `cd` to `/vagrant/catalog/` dir and run `python runserver.py`.
* This will bring up the web server at `http://localhost:8000/` - ![](https://cloud.githubusercontent.com/assets/6732675/14061759/b56a2da6-f345-11e5-8621-ce6ac5f3e499.png)

#### Access the app
From local machine goto `http://localhost:8000/restaurant`, this will bring up the app:
![](https://cloud.githubusercontent.com/assets/6732675/14061849/60ef9510-f348-11e5-97e9-9baad6a5c69a.png)


#### Features
##### Web
###### Browse Restaurant/Menu Items
Click on restaurant link to view menu items listed in that restaurant:
![](https://cloud.githubusercontent.com/assets/6732675/14062175/c81344f8-f352-11e5-91f2-9221291ecec6.gif)

###### Social Login
The app supports social login for `google` and `facebook`. Use existing accounts in `google` and `facebook` to register w/ the restaurant menu app:
![](https://cloud.githubusercontent.com/assets/6732675/14062331/4aa4347c-f358-11e5-828a-1c258707724b.gif)

###### Add New Restaurant
When user is logged in, user can add a new restaurant:
![](https://cloud.githubusercontent.com/assets/6732675/14062359/7173f910-f359-11e5-9d8a-72f937b39b0b.png)

###### Add Menu Items in Restaurant
**Owner of the Restaurant:**
If logged in user is the owner of the restaurant, he can add menu item in that restaurant:
![](https://cloud.githubusercontent.com/assets/6732675/14062394/76790e9a-f35a-11e5-9065-0afbd9976295.png)

**Not Owner of the Restaurant:**
Flash message is thrown if logged in user is not the owner of the restaurant:
![](https://cloud.githubusercontent.com/assets/6732675/14062418/364db824-f35b-11e5-9b98-bf57338acfbb.gif)

###### Update/Delete Menu Items
Logged in user can update or delete menu item if user is owner of the restaurant. If the user is not the owner of the restaurant, the dropdown link/caret is hidden on the menu item:
![](https://cloud.githubusercontent.com/assets/6732675/14062500/4b416aac-f35e-11e5-9b3a-b00a0a0425ae.gif)

###### Update/Delete Restaurant
Logged in user can update restaurant name or delete it if user is owner of the restaurant. If user is not the owner then the `Restaurant` dropdown on header is hidden for that restaurant:
![](https://cloud.githubusercontent.com/assets/6732675/14062520/0d9bd196-f35f-11e5-8281-4e61385c8f39.gif)


##### API
The app supports two API representation type (response data type) which are `application/json` and `application/xml`. Set `Accept` header type in the request to get desired `Content-Type`.

###### Retrieve Restaurant List
```
Endpoint: /api/v1.0/restaurant
Method: GET
```
JSON:
```
Accept: application/json
```
XML:
```
Accept: application/xml
```
![](https://cloud.githubusercontent.com/assets/6732675/14062646/761871da-f363-11e5-8446-46e5b3e98750.gif)

###### Retrieve Restaurant's Menu List
```
Endpoint: /api/v1.0/restaurant/<int:restaurant_id>/
Endpoint: /api/v1.0/restaurant/<int:restaurant_id>/menu
Method: GET
```
JSON:
```
Accept: application/json
```
XML:
```
Accept: application/xml
```

###### Retrieve Restaurant's Single Menu Item
```
Endpoint: /api/v1.0/restaurant/<int:restaurant_id>/menu/<int:menu_id>/
Method: GET
```
JSON:
```
Accept: application/json
```
XML:
```
Accept: application/xml
```
