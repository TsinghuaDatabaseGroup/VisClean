<p align="center">
  <a href="https://github.com/TsinghuaDatabaseGroup/VisClean/">
    <img
      alt="VisClean"
      src="https://github.com/TsinghuaDatabaseGroup/VisClean/blob/master/icon.png"
    />
  </a>
</p>


# VisClean v0.1
Data visualization is crucial in data-driven decision making. However, bad visualizations generated from dirty data often mislead the users to understand the data and draw wrong decisions. We propose VisClean, a system that progressively turns bad visualizations into good ones by interactive cleaning. The attendees will experience two main features: (1) Active Interaction: VisClean provides a novel window-based method that allows users to directly manipulate the visualizations (for bar/pie charts) to clean the data. (2) Passive Interaction: VisClean selects the most beneﬁcial and visualization-aware cleaning questions to the user and then reﬁnes the visualization (for bar/pie/line charts).

## Preview
![front-end-min](front-end-min.png)

## Architecture
<p align="center">
  <a href="https://github.com/TsinghuaDatabaseGroup/VisClean/">
    <img
      alt="Architecture"
      src="https://github.com/TsinghuaDatabaseGroup/VisClean/blob/master/architecture-min.png"
      width="65%"
    />
  </a>
</p>

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
- [x] [Node.js v8.2.1](https://github.com/nodejs/node) for web service
- [x] Python 3.6
- [x] [py_entitymatching](https://github.com/anhaidgroup/py_entitymatching/tree/rel_0.3.x) for EM


### Installing
Clone from Github
```
> https://github.com/TsinghuaDatabaseGroup/VisClean.git
> cd VisClean
```
Run Web Server
```
# Note that, the root directory should be /VisClean/ 
> cd  VisClean
> node web/bin/www
```
The VisClean could be visited at [http://localhost:8080](http://localhost:8080)


## What's new feature will in VisClean v0.2?
- A smarter inference algorithm from the answer of the user
- More friendly interaction and UI (Using Vue.js for font-end)
- Restruct the source code and release a development version for easily using in Ipython and PyPi package.

## Contributors
|#|Contributor|Affiliation|Contact|
|---|----|-----|-----|
|1|[Yuyu Luo](http://thanksyy.cn)| M.S. Student, Tsinghua University| luoyy18@mails.tsinghua.edu.cn
|2|[Chengliang Chai](http://dbgroup.cs.tsinghua.edu.cn/chaicl/)| PhD Candidate, Tsinghua University| chaicl15@mails.tsinhua.edu.cn
|3|[Guoliang Li](http://dbgroup.cs.tsinghua.edu.cn/ligl/)|Professor, Tsinghua University| LastName+FirstName@tsinghua.edu.cn
|4|[Nan Tang](http://da.qcri.org/ntang/index.html)|Senior Scientist, Qatar Computing Research Institute|ntang@hbku.edu.qa
|5|Xuedi Qin| PhD Student, Tsinghua University| qxd17@mails.tsinghua.edu.cn
##### If you have any questions or feedbacks about this project, please feel free to contact Yuyu Luo (luoyy18@mails.tsinghua.edu.cn).
