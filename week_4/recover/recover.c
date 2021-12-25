#include <stdio.h>
#include <stdlib.h>

typedef __int8_t BYTE;

typedef struct 
{
    __int32_t jpg_header;
    BYTE data[508];
} __attribute__((__packed__))
data_chunk;

// here the last 0 may be any number - so comapre only 28 bits
// warning in C integers in digits write in memory from end to start
__int32_t jpg_signature = 0xe0ffd8ff;

int main(int argc, char *argv[])
{
    // cli arguments check
    if (argc != 2)
    {
        fprintf(stderr, "usage: recove <name_of_raw_massive>\n");
        return 1;
    }
    
    // open memory card to read
    FILE *memory_card = fopen(argv[1], "r");
    if (memory_card == NULL)
    {
        fprintf(stderr, "can not open memory card file: %s\n", argv[1]);
        return 1;
    }

    // create pointer to file to write recover jpg
    FILE *rec_file = NULL;
    char file_name[8];

    // number to create filenames
    unsigned int rec_number = 0;

    int control_bytes_read;
    int control_bytes_write;

    data_chunk buffer;

    // main loop
    while (1)
    {
        control_bytes_read = 0;
        control_bytes_write = 0;
        buffer.jpg_header = 0x00000000;

        // read from card.raw file
        control_bytes_read = fread(&buffer, 1, sizeof(buffer), memory_card);

        // test read
        if (ferror(memory_card))
        {
            fprintf(stderr, "error than reding from file%s\n", argv[1]);
            return 1;
        }
        
        // if we get EOF and no need padding
        if (feof(memory_card) && control_bytes_read == 0)
        {
            break;
        }

        // if it is jpg file
        if ((buffer.jpg_header & 0xf0ffffff) == jpg_signature)
        {
            if (rec_file != NULL)
            {   
                fclose(rec_file);
            }

            sprintf(file_name, "%03i.jpg", rec_number);
            rec_number++;
            
            rec_file = fopen(file_name, "w");
            if (rec_file == NULL)
            {
                fprintf(stderr, "can not open to write restored file:%s\n", file_name);
                return 1;
            }
            
            control_bytes_write = fwrite(&buffer, 1, control_bytes_read, rec_file);      
        }

        // if it is not jpg file
        else
        {
            if (rec_file != NULL)
            {   
                control_bytes_write = fwrite(&buffer, 1, control_bytes_read, rec_file);
            }
        }
        
        // padding
        if (feof(memory_card) && control_bytes_read > 0)
        {
            if (control_bytes_write != sizeof(data_chunk) && rec_file != NULL)
            {   
                int bytes_to_pad = sizeof(data_chunk) - control_bytes_write;
                for (int i = 0; i < bytes_to_pad; i++)
                {
                    fputc(0x00, rec_file);
                }
            }
            // main loop
            break;
        }
       
    }
    
    // postproduction
    if (rec_file != NULL)
    {
        fclose(rec_file);
    }
    fclose(memory_card);
}
