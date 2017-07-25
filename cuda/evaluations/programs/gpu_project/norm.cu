#include<stdio.h>
#include<stdlib.h>
#include<sys/time.h>

#define BLOCK_SIZE 16
#define GRID_SIZE 160
#define SIZE BLOCK_SIZE*BLOCK_SIZE*GRID_SIZE*GRID_SIZE

void checkresult(float *ref, float *in, float *out, float *mul, int width){
	
	for(int i = 0 ; i < GRID_SIZE; i++){
		for(int j = 0; j < GRID_SIZE; j++){
			float sum = 0.0f;
			int start = j * BLOCK_SIZE * width + i * BLOCK_SIZE;
			for(int ii = 0; ii < BLOCK_SIZE; ii++){
				for(int jj = 0; jj < BLOCK_SIZE; jj++){
					sum += in[start + ii * width + jj] * mul[jj];
				}
			}
			for(int ii = 0; ii < BLOCK_SIZE; ii++){
				for(int jj = 0; jj < BLOCK_SIZE; jj++){
					if(jj % 2 == 0 && ii % 2 == 0)
						ref[(j * BLOCK_SIZE + jj) * width + i * BLOCK_SIZE + ii] = 2.0 * in[(j * BLOCK_SIZE + jj) * width + i * BLOCK_SIZE + ii]/sum;
					else if(jj % 2 == 1 && ii % 2 == 0)
						ref[(j * BLOCK_SIZE + jj) * width + i * BLOCK_SIZE + ii] = in[(j * BLOCK_SIZE + jj) * width + i * BLOCK_SIZE + ii]/sum;
					else if(jj % 2 == 1 && ii % 2 == 1)
						ref[(j * BLOCK_SIZE + jj) * width + i * BLOCK_SIZE + ii] = (-1.0) * in[(j * BLOCK_SIZE + jj) * width + i * BLOCK_SIZE + ii]/sum;
					else
						ref[(j * BLOCK_SIZE + jj) * width + i * BLOCK_SIZE + ii] = 0.0f;
				}
			}
		}
	}

	for(int i = 0; i < SIZE; i++){
		if(abs(ref[i]-out[i]) > 1.e-6){
			printf("results checking failed at %d ref %f out %f\n", i, ref[i], out[i]);
			return;
		}
	}
	printf("results checking passed!\n");
}

__global__ void norm(float *in, float *out, float *mul, int width){
	int tx = blockIdx.x * blockDim.x + threadIdx.x;
	int ty = blockIdx.y * blockDim.y + threadIdx.y;

	if(tx >= width || ty >= SIZE/width) return;
	int start = blockIdx.x * blockDim.x * width + blockIdx.y * blockDim.y;
	float sum = 0.0f;

	for(int i = 0; i < BLOCK_SIZE; i++){
		for(int j = 0; j < BLOCK_SIZE; j++){
			sum += in[start + i * width + j] * mul[j];
		}
	}
	if(tx % 2 == 0 && ty % 2 == 0)
		out[tx * width + ty] = 2.0 * in[tx * width + ty]/sum;
	else if(tx % 2 == 1 && ty % 2 == 0)
		out[tx * width + ty] = in[tx * width + ty]/sum;
	else if(tx % 2 == 1 && ty % 2 == 1)
		out[tx * width + ty] = (-1.0) * in[tx * width + ty]/sum;
	else
		out[tx * width + ty] = 0.0f;

}



int main(){
	float *hA_in = (float *)malloc(SIZE * sizeof(float));
	float *hA_out = (float *)malloc(SIZE * sizeof(float));
	float *hB_in = (float *)malloc(BLOCK_SIZE * sizeof(float));
	float *ref = (float *)malloc(SIZE * sizeof(float));
	float *dA_in, *dA_out, *dB_in;

	srand(2016);

	for(int i = 0; i < SIZE; i++){
		hA_in[i] = (float)rand()/(float)RAND_MAX;
	}
	for(int i = 0; i < BLOCK_SIZE; i++){
		hB_in[i] = (float)rand()/(float)RAND_MAX;
	}

	cudaMalloc((void **)&dA_in, SIZE * sizeof(float));
	cudaMalloc((void **)&dA_out, SIZE * sizeof(float));
	cudaMalloc((void **)&dB_in, BLOCK_SIZE * sizeof(float));

	cudaMemcpy(dA_in, hA_in, SIZE * sizeof(float), cudaMemcpyHostToDevice);
	cudaMemcpy(dB_in, hB_in, BLOCK_SIZE * sizeof(float), cudaMemcpyHostToDevice);
	struct timespec start, end;	
	dim3 grid(GRID_SIZE, GRID_SIZE, 1);
	dim3 block(BLOCK_SIZE, BLOCK_SIZE, 1);
	cudaDeviceSynchronize();
	clock_gettime(CLOCK_REALTIME, &start);

	norm<<<grid, block>>>(dA_in, dA_out, dB_in, BLOCK_SIZE * GRID_SIZE);

	cudaDeviceSynchronize();
	clock_gettime(CLOCK_REALTIME, &end);

	printf("kernel time %fs\n", end.tv_sec - start.tv_sec + (end.tv_nsec - start.tv_nsec)/1.e9);
	cudaMemcpy(hA_out, dA_out, SIZE * sizeof(float), cudaMemcpyDeviceToHost);
	checkresult(ref, hA_in, hA_out, hB_in, BLOCK_SIZE * GRID_SIZE);

}
