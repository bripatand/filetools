#!/bin/bash

ffmpeg -i "/mnt/c/DATA/ToBeDeleted/FaceAuCouteau/9-Attaque de cote.mp4" -vf scale=1080:720 -crf 20 -c:a copy "/mnt/c/Users/pb/Videos/Sport/Kravmaga/KravMagaGlobalFR/FaceAuCouteau/9-Attaque de cote.mp4"
