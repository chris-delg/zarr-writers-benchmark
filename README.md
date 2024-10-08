# Benchmarking Zarr Writers 

This benchmarking suite compares the following Zarr writers (click for documentation): 
- [TensorStore](https://google.github.io/tensorstore/)
- [Zarr-Python](https://zarr.readthedocs.io/en/stable/index.html)
- [OME-Zarr](https://ome-zarr.readthedocs.io/en/stable/)
- [Cpp Zarr](https://github.com/abcucberkeley/cpp-zarr)

## Building and Running

To build and run the benchmark in this program, you need to install the various Zarr writers on your machine. Refer below to see what options you have for your operating system.

### Linux (Tested on Ubuntu 22.04)

Linux users also have the option to use Docker, so if you would like to do so please refer below to the Mac and Windows instructions.<br><br>
Before running the script, make sure you have these requirments satisfied:

+ Cpp Zarr installed from source (see link above)
+ [Pybind11](https://pybind11.readthedocs.io/en/stable/installing.html)
+ [Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)
  
An "environment.yml" has been provided for simplifying the dependency process on Linux. Execute the following commands to download the dependencies using Conda.
```bash
conda env create -n benchmark --file environment.yml
conda activate benchmark
```
Next run the setup script to build the cpp code.
```bash
./setup.sh
```
Finally, run the benchmark using Python.
```bash
python main.py
```

### Mac and Windows

Since some of the dependencies are only available on Linux, a Dockerfile has been left to allow building on other systems. Simply download [Docker](https://www.docker.com/) and execute the following commands to run the program. Please note that when running the program using Docker, 

```bash
docker build -t benchmark .
docker run -it benchmark
```

## Usage
The Benchmark class located in [benchmark.py](https://github.com/acquire-project/zarr-writers-benchmark/blob/main/benchmark.py) holds the main logic of how to run the tests. The code in [main.py](https://github.com/acquire-project/zarr-writers-benchmark/blob/main/main.py) holds an example of how to run the tests and view the data using matplotlib graphs.

### Running All Tests
The "run_all_tests" method runs both the append tests and the write tests.
```python
def run_all_tests(
  self,
  append_test_gigabytes: int,
  write_test_gigabytes: int, 
  choose_lib: Optional[str] = None,
  append_graph: Optional[matplotlib.axes._axes.Axes] = None,
  append_avg_graph: Optional[matplotlib.axes._axes.Axes] = None,
  write_graph: Optional[matplotlib.axes._axes.Axes] = None,
  write_avg_graph: Optional[matplotlib.axes._axes.Axes] = None
) -> None:
```
Required arguments:
+ <strong>append_test_gigabytes</strong> : int acting as a soft cap for the amount of data written out during the append tests.
+ <strong>write_test_gigabytes</strong> : int acting as a soft cap for the amount of data written out during the write tests.

Optional arguments:
+ <strong>choose_lib</strong> : string representing the library you want to test. If not specified, all libraries will be tested.
+ <strong>append_graph</strong> : matplotlib graph that will plot the data for the append tests.
+ <strong>append_avg_graph</strong> : matplotlib graph that will plot the average GBps for each library in the append tests.
+ <strong>write_graph</strong> : matpllotlib graph that will plot the data for the write tests.
+ <strong>write_avg_graph</strong> : matplotlib graph that will plot the average GBps for each library in the write tests.

### Running Write Tests
The "run_write_tests" method runs the write tests.
```python
def run_write_tests(
  self,
  num_of_gigabytes: int,
  show_results: bool,
  choose_lib: Optional[str] = None,
  graph: Optional[matplotlib.axes._axes.Axes] = None, 
  avg_graph: Optional[matplotlib.axes._axes.Axes] = None
) -> None:
```
Required arguments:
+ <strong>num_of_gigabytes</strong> : int acting as a soft cap for the amount of data written out during the write tests.
+ <strong>show_results</strong> : bool indicating whether you want the result of the tests printed to the terminal.

Optional arguments:
+ <strong>choose_lib</strong> : string representing the library you want to test. If not specified, all libraries will be tested.
+ <strong>graph</strong> : matplotlib graph that will plot the data for the write tests.
+ <strong>avg_graph</strong> : matplotlib graph that will plot the average GBps for each library in the write tests.

### Running Append Tests
The "run_append_tests" method runs the append tests.
```python
def run_append_tests(
  self,
  num_of_gigabytes: int,
  show_results: bool,
  choose_lib: Optional[str] = None,
  graph: Optional[matplotlib.axes._axes.Axes] = None, 
  avg_graph: Optional[matplotlib.axes._axes.Axes] = None
) -> None:
```
Required arguments:
+ <strong>num_of_gigabytes</strong> : int acting as a soft cap for the amount of data written out during the append tests.
+ <strong>show_results</strong> : bool indicating whether you want the result of the tests printed to the terminal.

Optional arguments:
+ <strong>choose_lib</strong> : string representing the library you want to test. If not specified, all libraries will be tested.
+ <strong>graph</strong> : matplotlib graph that will plot the data for the append tests.
+ <strong>avg_graph</strong> : matplotlib graph that will plot the average GBps for each library in the append tests.

## Benchmark Notes (08/21/24)

Please note that these observations are dynamic and may change if there are updates to the Zarr libraries being tested.<br>

The benchmarking data was collected using Ubuntu 22.04 on a machine with the following hardware:

+ Intel i7 11700k processor
+ 32 gigabytes of ram running at 3600MHz
+ NVIDIA GeForce RTX 3070
+ WD_BLACK 1TB SN850X NVMe m.2

### Testing Methodology
There were two types of tests ran in this benchmarking suite, append tests for the libraries that supported an append functionality, and a write test. In both of these tests, data would be continuously written until it reached a multiple of the original specified size.<br>

For example, if we had a starting shape of [64, 1080, 1920] and we wanted to write out 50GBs, a multiplier that increases after every write would be multiplied to the first dimension of the shape.<br>
+ First Write : multiplier = 1, shape = [64 * multilplier, 1080, 1920]
+ Next Write : multiplier = 5, shape = [64 * multiplier, 1080, 1920]

The difference between the two tests lies in the type of writes we were doing. In the append test, only one Zarr folder was created, which would then have data continuously appended to the back of it until it reached the desired size. For these tests, we would graph the speed of the write (GBps) vs. the current write number. In the write tests, we would create multiple Zarr folders, each slightly larger than the last, until we reached the desired size. For these tests, we would graph the speed of the write (GBps) vs. the amount of data being written.<br>

A consistent starting shape size, chunk size, and compressor were used for all of the libraries during each test to remove as much variability as possible.

### Observations
For these notes the following was specified for the zarr libraries:
+ shape = [64, 1080, 1920]
+ chunks = [64, 540, 1920]
+ LZ4 compression
+ C order data

Ranking from fastest to slowest in append tests:
+ TensorStore → 1.46 average GBps
+ Zarr Python → 0.74 average GBps

Ranking from fastest to slowest in write tests:
+ TensorStore → 2.37 average GBps
+ Zarr Python → 2.02 average GBps
+ OME Zarr $~~~$ → 0.29 average GBps
+ Cpp Zarr $~~~$ → 0.19 average GBps

<strong>Memory Usage / Threads:</strong><br>

For the following notes, I will be using ratios like 1:1, 3:1, etc., to represent how much memory Python is using versus how much data is being written out. For example, if I have a ratio of 2:1, it means Python takes up 2 GB for every 1 GB of data being written, indicating that some level of data copying is occurring. These ratios help us understand how memory efficient these Zarr libraries are and can help us draw conclusions about their performance in comparison to one another.<br>

<strong>TensorStore :</strong> Around 3:1 memory usage and a consistent utilization of 59 threads.<br>
<strong>Zarr Python :</strong> Around 2:1 memory usage and a consistent utilization of 26 threads.<br>
<strong>OME Zarr :</strong> Around 5:1 memory usage and a consistent utilization of 26 threads.<br>
<strong>CPP Zarr :</strong> Around 2:1 memory usage and a consistent utilization of 41 threads.<br>

<strong>Features:</strong><br>

Please note that this is just a list of notable features, highlighting those that are present or absent. For a comprehensive list of all features, please refer to the documentation.

<strong>TensorStore :</strong> Offers S3 support, Google Cloud Storage support, local filesystem support, ZarrV3 support, and the ability to append data.<br>
<strong>Zarr Python :</strong> Offers S3 support, local filesystem support, ZarrV3 support, and the ability to append data.<br>
<strong>OME Zarr :</strong> Offers S3 support and ZarrV3 support, but does not offer the ability to choose a compressor, and does not let you append data.<br>
<strong>Cpp Zarr :</strong> Offers local filesystem supoort and matlab support.<br>

### Conclusions
<strong>TensorStore</strong>
+ Decent memory efficiency with a memory usage of 3:1, indicating that a decent amount of copying is occurring. However, there is great use of multithreading, with 59 threads being utilized.
+ Memory usage makes it less efficient than Zarr Python in that category, but it makes up for this with the number of threads it uses, which is almost three times the amount used by OME Zarr and Zarr Python.
+ Overall, this leads to TensorStore being the best-performing library in terms of write speeds among those tested.

<strong>Zarr Python</strong>
+ Great memory efficiency with a memory usage of 2:1 and a decent amount of multithreading, with the library utilizing 26 threads.
+ This leads to efficient writes placing it firmly as one of the top performers in terms of write speeds.
+ Comes with built in functionality for appending data that handles everything under the hood which makes it really straight forward and easy to do so, unlike TensorStore which requires more effort. 

<strong>OME Zarr</strong>
+ Worst memory efficiency of the group, with a memory usage of 5:1, indicating that a large amount of data is being copied during the write process, while using about the same number of threads as Zarr Python.
+ The memory inefficiencies significantly reduce performance, leading OME Zarr to have relatively slow average write speeds compared to the best-performing libraries.
+ Memory inefficiencies affect performance in more ways than just write speeds. Due to the amount of data copying, a large amount of pressure is put on the RAM and swap, causing OME Zarr to crash the program much sooner than the other libraries.

<strong>Cpp Zarr</strong>
+ Tied with Zarr Python in terms of memory efficiency making it very efficient in that category.
+ Utilizes 41 threads which puts it in the middle of the pack compared to the libraries tested.
+ Cpp Zarr was built for working with F order data so when using C order data its performance drops off dramatically, leaving it to be the worst perfroming library tested. Homever, if working with F order data, Cpp Zarr boasts the best write speeds out of the bunch.
