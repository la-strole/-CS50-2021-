// Modifies the volume of an audio file

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

// Number of bytes in .wav header
const int HEADER_SIZE = 44;
unsigned long int read_number, write_number;

int main(int argc, char *argv[])
{
    // Check command-line arguments
    if (argc != 4)
    {
        printf("Usage: ./volume input.wav output.wav factor\n");
        return 1;
    }

    // Open files and determine scaling factor
    FILE *input = fopen(argv[1], "r");
    if (input == NULL)
    {
        printf("Could not open file.\n");
        return 1;
    }

    FILE *output = fopen(argv[2], "w");
    if (output == NULL)
    {
        printf("Could not open file.\n");
        return 1;
    }

    float factor = atof(argv[3]);

    // TODO: Copy header from input file to output file

    int8_t *header;
    // number of bytes on .wav header of data size
    const int data_size_byte_number = 4;
    
    header = malloc(HEADER_SIZE - data_size_byte_number);

    if (header == NULL)
    {
        printf("Allocation error.");
        return 1;
    }

    int32_t data_size;
    
    read_number = fread(header, HEADER_SIZE - data_size_byte_number, 1, input);
    if (read_number != 1)
    {
        if (ferror(input))
        {
            printf("error during reading file");
            return 1;
        }
        else if (feof(input))
        {
            printf("EOF than reading file");
            return 1;
        }
        printf("undefined error than reading file");
        return 1;
    }
    write_number = fwrite(header, HEADER_SIZE - data_size_byte_number, 1, output);
    if (write_number != read_number)
    {
        printf("write error");
        return 1;
    }
    free(header);

    // read and write data size
    fread(&data_size, sizeof(data_size), 1, input);
    fwrite(&data_size, sizeof(data_size), 1, output);
    
    // TODO: Read samples from input file and write updated data to output file
      
    int16_t sample;
    
    read_number = 0;
    write_number = 0;
    
    while (1)
    {
        read_number += fread(&sample, sizeof(sample), 1, input);
        
        if (feof(input))
        {
            break;
        }

        if ((sample * factor) > 32767 || (sample * factor) < -32767)
        {
            printf("too loud");
            return 1;
        }
        else
        {
            sample = sample * factor;
        }

        write_number += fwrite(&sample, sizeof(sample), 1, output);
    }
    
    //test
    // printf("total read =%lu, total write =%lu, total_samples=%i\n", read_number, write_number, data_size / 2);
    
    // Close files
    fclose(input);
    fclose(output);
}
