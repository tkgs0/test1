#!/bin/bash

cd ~/Zero && git reset --hard && git pull && screen -dmS goo
sleep 5
screen -r goo -X stuff "vim ~/Zero/plugin/qqwife/command.go\n"
sleep 3
screen -r goo -X stuff ":%s/favor < 30/favor < 50/g\n"
sleep 3
screen -r goo -X stuff ":%s/favor < 20/favor < 50/g\n"
sleep 3
screen -r goo -X stuff ":%s/favor = 30/favor = 50/g\n"
sleep 3
screen -r goo -X stuff ":%s/favor = 10/favor = 50/g\n:wq\n"
sleep 3
screen -r goo -X stuff "vim ~/Zero/plugin/aipaint/aipaint.go\n"
sleep 3
screen -r goo -X stuff ":%s/token=%v/token=%v\\&r18=1/g\n:wq\n"
sleep 3
screen -r goo -X stuff "vim ~/Zero/plugin/thesaurus/chat.go\n"
sleep 3
screen -r goo -X stuff ":%s/seg))/seg), zero\\.OnlyToMe)/g\n:wq\n"
sleep 3
screen -r goo -X quit && go mod tidy && go build -ldflags "-s -w" -trimpath -o zbp && GOOS=windows GOARCH=amd64 go build -ldflags "-s -w" -trimpath -o zbp.exe && cp zbp.exe /setu/ && screen -r zbp -X quit
sleep 3
cp zbp ~/bot/zbp/

