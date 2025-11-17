// workload_mix.c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <pthread.h>

#define N 2000000

void *cpu_intensive(void *arg) {
    volatile long s = 0;
    for (int i = 0; i < N; ++i) s += (i & 0xff) - (i & 0x0f);
    printf("int done %ld\n", s);
    return NULL;
}

void *fp_intensive(void *arg) {
    double x = 1.0;
    for (int i = 0; i < N; ++i) x = x * 1.0000001 + sin(i%10);
    printf("fp done %f\n", x);
    return NULL;
}

void *mem_intensive(void *arg) {
    int *A = malloc(sizeof(int) * N);
    for (int i = 0; i < N; ++i) A[i] = i;
    long s = 0;
    for (int i = 0; i < N; i += 16) s += A[i];
    printf("mem done %ld\n", s);
    free(A);
    return NULL;
}

int main() {
    pthread_t t1, t2, t3;
    pthread_create(&t1, NULL, cpu_intensive, NULL);
    pthread_create(&t2, NULL, fp_intensive, NULL);
    pthread_create(&t3, NULL, mem_intensive, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    pthread_join(t3, NULL);
    printf("all done\n");
    return 0;
}
