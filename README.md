This currently only allows you to control the devices. 

To use this, you must create a account via the Oakter app and setup your device with your phone. 

It is recomended that you create a specific account and link the devices to it as well for using this tool as you might have to face inconvinience when using the mobile app from the same account. 

After creating an account use HTTPToolkit in your phone and PC to intercpt http requests. After the interception starts working, logout and login into your account. Then you will observe a post request to `http://live.oakter.com:8899/OakterRestService.svc/Login` in your PC. Its headers will appear like:

```
{
  "OS": "A",
  "OS_Version": "",
  "Version": "",
  "App_Version": "",
  "Brand": "",
  "User": {
    "Token": "",
    "About": {
      "Model": "",
      "Manufacturer": ""
    }
  },
  "Username": ""
}
```

Now you just have to copy the "Token" from this and the "Username"

Put the values of both of these in the JSON file which is present along with the Oakter file

Leave SID as it is, it is only required for you to enter username and token.
