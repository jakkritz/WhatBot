# WhatBot Frontend
This package contains the frontend of WhatBot. In production mode, uWSGI and nginx web server are used for to run the the React app in a more stable and optimize performance. You can see `npm run build` for more details on why. In deployment, production mode is used and the `Dockerfile`' and nginx used is only configured to work on HTTPS server so we have only provided instruction on how to run locally here as using *Docker* to run locally will not work.  

## Setup, build and run
**Running locally**  
*Prerequisites*: npm installed  
Setup
```
npm install
```
Run:
```
npm start
```

### Other Available Scripts

In the project directory, you can run:

#### `npm start`

Runs the app in the development mode.<br>
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br>
You will also see any lint errors in the console.

#### `npm test`

Launches the test runner in the interactive watch mode.<br>
We are using mocha with chai-enzyme for testing. This will 
mock various services and component rendering.

#### `npm run ttd`

Launches the test runner fom `npm test` in TTD mode. 


#### `npm run build`

Builds the app for production to the `build` folder.<br>
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br>
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.
