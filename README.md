# YACK Automated Comic Kreator
**Hack Cambridge 2022**

Deepgram api is used for speech-to-text, get your key at https://deepgram.com and put it into `./.secrets` as
```env
DEEPGRAM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

dlib Facial Landmark Detector is used, which is available under the Boost Software License
from https://github.com/davisking/dlib. The pretrained weights used are available
from http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2 and should be placed
in `./src/dlib_shape_predictor/`.

To start developing using Docker, simply use
```shell
make run
```

Alternatively, create a virtual environment, and use
```shell
make install
```
