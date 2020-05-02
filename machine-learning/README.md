# Study for ML

## folder info
    ├── bin/                           # script for running docker container  
    ├── notebooks 
    |       ├── intro-deep-learning    # memo about the 「ゼロから作るDeep Learning」 
    |       └── udemy                  # memo about the 「実践 Python データサイエンス」 
    ├── scripts/                 
    |       ├── deep-learning-lecture  # code about the deep learning lecture
    |       └── ml-methods             # algorithm implementation about basic ML methods  
    ├── Dockerfile  
    └── README.md  

# setup 

```
$ docker build . -t machine-learning
```

## 対話型

対話型で Python スクリプトを実行

```
$ bash bin/docker-run.sh
```

## Jupyter

jupyter notebook を使う時のコマンド

```
/* confirm container */
$ docker ps -a

/* if container already exists */
$ docker start jn
$ docker stop jn

/* create container */
$ bash bin/note-run.sh

/* confirm password */
$ docker exec -i -t jn bash
$ jupyter notebook list
```
