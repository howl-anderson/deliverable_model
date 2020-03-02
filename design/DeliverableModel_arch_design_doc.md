# DeliverableModel 设计文档
版本：1.0
## 设计目标
### 问题陈述
模型部署涉及到前置和后置处理逻辑以及DNN模型，部署过程涉及到依赖的安装和代码的发布，过程复杂而且不统一，耗时耗力。

### 目标
为了更加快速的部署，特别设计 Deliverable Model 模型。Deliverable Model 以模型文件和SDK的方式存在，提供和信道无关的面向对象的功能。追求让部署变成黑盒操作和开箱即用，同时也不会对模型生产者构成很大的工作负担。

Deliverable Model 支持 All In Local 模式和 Remtoe Wraper 模式。

All I Local 模式是指模型全部都在本地，通常都在一个进程内。部署流程非常简单，适合测试和演示等非生产环境的使用。

Remote Wrapper 模式是指模型的前置和后置处理部分在一个进程内，DNN模型部分在另一个进程（通常是基于docker的 TensorFlow serving）。可以取得最大化的性能，适用于生产环境。

## DeliverableModel 格式规范


### metadata.json

用于存储模型的构建信息：

* 当前 DeliverableModel 的版本，目前的版本为 1.0
*   process 用的什么
*   模型使用的是什么
*   关于模型的算法和语料的信息

实现：

```json
{
    "version": "1.0"
    "dependency": [
        "package_a >= min_version < max_version"
    ]
    "model": {
        "type": "tensorflow_saved_model",
        "version": "1.0"，
        "custom_object_dependency": [],
        "converter_for_request": "",
        "converter_for_response": ""
    }
    "processor": {
        "version": "1.0"
        "instance": {
            "processor_a": {
                "class": "class_name",
                "parameter": {}
            },
            "processor_b": {
                "class": "class_name",
                "parameter": {}
            }
        },
        "pipeline": {
            "pre": [
                "processor_a",
                "processor_b"
            ],
            "post": [
                "processor_b",
                "processor_a",
            ]
        }
    },
    "metadata": {
        "version": "1.0"
        "id": "AlgorithmID-CorpusID-ConfigureID-RunID"
    }
}
```




#### DeliverableModel 容器

容器最重要的字段是 version 表示当前的 DeliverableModel 的版本，在解析 metadata.json 时应检查版本，确保兼容。当前版本为 ”1.0“。

1.0 版本的 DeliverableModel 包含三个子容器：model、processor 和 metadata。后有详述。


#### dependency

指定该模型的依赖，列表，每个 item 和 requirements.txt 的一行 格式类似


#### model

model 容器定义了当前 DeliverableModel 所使用的模型。model 容器有三个字段：type 、custom_object_dependency、converter_for_request、converter_for_response 和 version。type 定义了模型的类型，对应后续的 backend；custom_object_dependency 表示所依赖的自定义组件；converter_for_request、converter_for_response 分别定义了模型推理前后的最后转化函数，表示如何将 request 对象转换成模型可以直接使用的原始数据，以及将模型输出的原始结果转换成 response 对象。函数使用文件的形式序列化下来。而 version 字段用于表示当前序列在磁盘中的模型的格式版本。不同的版本间可能不兼容。


#### processor

对于有前置（preprocessor）和后置（postprocessor）处理需求的模型。processor 容器定义了预处理的方法和步骤，包含三个字段：version、instance 和 pipeline。verision 用于标志兼容性。instance 用于表示如何实例化 processor。instance 是一个字典，key 表示实例的名字，value 是一个字典，被称之为 build block。 build block 是一个字典结构，拥有 class 和 parameter 两个 key。class 用于表示被实例化的类的 FQN。parameter 是一个字典，就是实例化类时的 **kwargs。pipeline 分为两个部分：pre 和 post 分别代表前置（preprocessor）和后置（postprocessor）处理。每个处理部分都是有序列表，每个元素都对应 instance 中的每实例。在前置（preprocessor）pipeline 中，每个实例的 preprocess 方法会被调用。在后置（postprocessor）pipeline 中，每个实例的 postprocess 方法会被调用。无论是哪种调用方式，Request (下文有解释) 会被传入 preprocess 或者 postprocess，并期望返回 Request。


#### metadata

metadata 用于表示这个模型的特性，所用的：代码、语料和参数。verision 用于标志兼容性。当前版本 1.0。当前版本只有一个字段：id，字符串类型。id 由三个 “-” 分割成四个部分。第一部分是：AlgorithmID，用于标志算法代码。第二部分是：CorpusID，用于标志语料。第三部分：ConfigureID，用于标志配置。第四部分：RunID，用于标志具体的执行。


### processor（处理器）

一个 Python 模块，需要加入搜索路径，用于自动载入。


### Model Loader

其他目录，这些目录会被模型载入器使用。目前预定义的三个 model loader 是


#### tensorflow_saved_model

模型所在的目录 tensorflow_saved_model， 内容为标准的 SavedModel。


#### keras_saved_model

模型所在的目录 keras_saved_model， 内容为 keras 版本的 SavedModel。


#### keras_h5_model

模型所在的目录 keras_saved_model， 内容为 keras_model.h5。


## API 接口规范
### 接口定义

### load 接口

输入：模型格式的路径（目录）

输出：DeliverableModel 模型对象


### parse 接口

输入：Request 对象

输出： 对象


### metadata 接口

输入：无

输出：MetaContent 对象

### 伪代码演示
#### All In Local 模式
部署者的 Deliverable Model 这里假设其路径为 /path/to/deliverable_model。

他应该可以使用如下接口进行处理：

```python
from deliverable_mode import ModelInference

mi = ModelInference("/path/to/deliverable_model")
result = mi.parse("查询明天的天气")
print(result)  # result 是一个 PredictInfo 对象，部署者可以从中获得请求结果或者异常信息
```

#### Remote Wrapper 模式
部署者的 Deliverable Model 这里假设其路径为 /path/to/deliverable_model。

##### 启动 DNN 模型
###### 获得 saved_model 路径

执行
```bash
python -m deliverable_model.get_saved_model /path/to/deliverable_model
```

将得到 saved_model 的路径地址，假设为 /path/to/deliverable_model/saved_model

###### 启动 TensorFlow Serving

```bash
docker run -t --rm -p 8501:8501 -p 8500:8500 -v "/path/to/deliverable_model/saved_model:/models/ner" -e MODLE_NAME=ner google/tensorflow-serving --enable_batching --batching_parameters_file="/models/ner/batching_parameters_file"
```

##### 使用 Remote Wrapper
```python
import os

from deliverable_mode import ModelInference

os.environ["REMOTE_TF_SERVING"] = "grpc://ner:serving_default@localhost:8500"

mi = ModelInference("/path/to/deliverable_model")
result = mi.parse("查询明天的天气")
print(result)  # result 是一个 PredictInfo 对象，部署者可以从中获得请求结果或者异常信息
```