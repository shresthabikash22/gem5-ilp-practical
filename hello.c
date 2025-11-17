#include <stdio.h>
int main() {
    long sum = 0;
    for (long i = 0; i < 1000000; i++) {
        sum += i;
    }
    printf("Sum: %ld\n", sum);
    return 0;
}