# AR Server

To handle the client request to localize a landmark from image.

### Setup environment

Run

```bash
sudo apt update && sudo apt install -y libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx
```

Download & install custom [Hierarchical Localization](https://github.com/codemaker2015/Hierarchical-Localization) package. (Slightly modified from version 1.3)

```bash
git clone --recursive https://github.com/codemaker2015/Hierarchical-Localization
cd Hierarchical-Localization
pip install -e .
pip install --upgrade plotly
cd ..
```

Download [Image Dataset](https://github.com/codemaker2015/Wayfinder-App/Server/dataset.zip)

### Run the trainer script

```bash
python my_hloc.py
```

This process would take roughly ~10 minutes. At the end, you would get something like:
```console
[2023/08/30 02:47:32 hloc INFO] Reconstruction statistics:
Reconstruction:
        num_reg_images = 57
        num_cameras = 1
        num_points3D = 2656
        num_observations = 14258
        mean_track_length = 5.36822
        mean_observations_per_image = 250.14
        mean_reprojection_error = 0.971601
        num_input_images = 70
```

### Start the server

```bash
python app.py
```

The server will run on localhost:5000

### Test the API

Use the Thunder Client installed (the lightning icon). Import the sample `thunder-collection_Hloc API.json` to Thunder Client.

Try run the `Hloc API/Localize me` request.

So, the expected result is as follows:

```
{
  "result": "Conference Room A"
}
```

To test with your image, decode the image to Base64. You might want to resize to 512*512 px first. You can use [Image to Base64 encoder](https://base64.guru/converter/encode/image)

### Assign to application

You have two options, either update from the source code or from the app settings.

From **source code**, navigate to `Assets/Scripts/LocalizationSettings.cs` and update `serverUrl` player prefs default value.
 
Or, in app in localization page, open the **localization setting** and update the URL directly.

## Limitations and known issues

- Sometimes, when you send image from client, the server will respond `400` error or other error. Try kill and restart the server (you may need to do it few times), the server will fix itself. You can also test with Insomnia or Postman to debug the request.
- The server can handle only one request at a time. _Well technically this Flask server can handle concurrent users_, but the `image` endpoint (localization process) can only run single process at one time.
