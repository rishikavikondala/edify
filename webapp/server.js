const express = require('express');
const fileUpload = require('express-fileupload');
const postmark = require("postmark");
const request = require('request');
const {Storage} = require('@google-cloud/storage');

const app = express();

app.use(express.static('client'));
app.use(fileUpload());

async function execute (req, res) {
    // initialize Storage object
    const storage = new Storage({
        projectId: 'class-analysis-2020',
    });
    const BUCKET_NAME = 'zoom-files';
    const path = '' + Date.now() + '/';
    // initialize bucket
    const bucket = storage.bucket(BUCKET_NAME);
    // set file names
    const videoFileName = path + 'video.mp4';
    const transcriptFileName = path + 'transcript.txt';
    const chatFileName = path + 'chat.txt';
    // initialize files with the determines file names
    const videoFile = bucket.file(videoFileName);
    const transcriptFile = bucket.file(transcriptFileName);
    const chatFile = bucket.file(chatFileName);
    // upload the three files
    await upload(videoFile, req.files.video.data, videoFileName);
    await upload(transcriptFile, req.files.transcript.data, transcriptFileName);
    await upload(chatFile, req.files.chat.data, chatFileName);
    // make the three files publicly accessible via Storage bucket URL
    await videoFile.makePublic();
    await transcriptFile.makePublic();
    await chatFile.makePublic();
    // call the main Cloud Function
    await makeReq(req.body.email, path.substring(0, path.length - 1));
    // display confirmation page
    res.sendFile('confirmation.html', {root: __dirname + '/client/'});
}

async function makeReq(userEmail, bucketFolder) {
    // https://flaviocopes.com/node-http-post/
    request.post('[INSERT URL FOR GOOGLE CLOUD FUNCTION]', {
        json: {
            email: userEmail,
            folder_name: bucketFolder
        }
    }, (error, res, body) => {
        if (error) {
            console.error(error)
            return
        }
        console.log(body)
    })
}

async function upload(file, buffer, fileName) {
    return new Promise((resolve) => {
        file.save(buffer, { destination: fileName }, () => {
            resolve();
        });
    });
}

app.post('/process', [execute]);

app.listen(process.env.PORT || 5000)
