# nvvp-reports

The folder contains the nvvp reports and ground truth responses used in the quantitative experiments and also the program used in the case study. 
 

## 1. Folder: programs
### 1.1 Folder: mem_coalesced
	trans.cu: memory access for stores is not coalesced;
	trans_opt.cu: uses 2D surface memory for writting.
#### To compile:
	make
#### To run:
	./run.sh	

### 1.2 Folder: thread_divergence
	setmat.cu: has thread divergency problem in kernel reset_kernel;
	setmat_opt.cu: avoid if-else conditions to avoid the thread divergency;

#### To compile:
	make
#### To run:
	./run.sh

### 1.3 Folder: gpu_project
	norm.cu: a program that makes some normalization to values in a matrix.


	
## 2. Folder: report-gnd
ground truth responses for the nvvp reports for four programs:
* trans.cu
* trans_opt.cu
* knnjoin.cu
* knnjoin_opt.cu

## 3. Files: five NVVP reports

 






