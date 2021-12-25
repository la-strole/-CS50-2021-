#include "helpers.h"
#include <math.h>
#include <stdlib.h>
#include <stdio.h>

#define min(a,b) \
  ({ __typeof__ (a) _a = (a); \
      __typeof__ (b) _b = (b); \
    _a < _b ? _a : _b; })

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{   
    RGBTRIPLE *pixel;
    for (int row = 0; row < height; row++)
    {
        for (int col = 0; col < width; col++)
        {
            pixel = &image[row][col];
            // gray color - mean value from RGB pixel's values
            int gray_color = roundf(((*pixel).rgbtBlue + (*pixel).rgbtGreen + (*pixel).rgbtRed) / (float)3);
            // change pixel's RGB values to gray value
            (*pixel).rgbtBlue = gray_color;
            (*pixel).rgbtGreen = gray_color;
            (*pixel).rgbtRed = gray_color;
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{   

    RGBTRIPLE tmp;
    for (int row = 0; row < height; row++)
    {
        // find the middle of line and switch pixels
        for (int col = 0; col < (int)(width / 2); col++)
        {
            tmp = image[row][col];
            image[row][col] = image[row][width - col - 1];
            image[row][width - col - 1] = tmp;
        }
    }
    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{   

    // Allocate memory for buffer image - line size = (3 px * width) to make shure that processed pixels have no effect to neighbors
    int buffer_size = 3;
    
    RGBTRIPLE(*buffer)[width] = calloc(buffer_size, width * sizeof(RGBTRIPLE));
    if (buffer == NULL)
    {
        fprintf(stderr, "Not enough memory to store image.\n");
        return;
    }

    // number of written lines - buffer count is row here
  
    for (int row = 0; row < height; row++)
    {
        // write buffer line to image if row > 3 (3 - buffer_size)
        if (row - buffer_size >= 0)
        {   
            for (int column = 0; column < width; column++)
            {   
                image[row - buffer_size][column] = buffer[row % 3][column];
            }
            // test
            // printf("write line from buffer on image=%i, buffer_ptr=%i\n", row - buffer_size, row % 3);
        } 

        for (int col = 0; col < width; col++)
        {
            // create 9pixels box and calculate sum rgb and number of pixels in box as divisor
            int divisor = 0;
            // sum_pix to sum values in box of pixels
            int sum_pix_rgbtBlue = 0;
            int sum_pix_rgbtGreen = 0;
            int sum_pix_rgbtRed = 0;

            // calculate divisor - number of valid pixels in 3*3 box and sum rgb
            for (int r = row - 1; r <= row + 1; r++)
            {
                for (int c = col - 1; c <= col + 1; c++)
                {
                    
                    // if pixel of box out of image
                    if (r < 0 || c < 0 || r > height - 1 || c > width - 1)
                    {
                        continue;
                    }
                    else
                    {
                        sum_pix_rgbtBlue += image[r][c].rgbtBlue;
                        sum_pix_rgbtGreen += image[r][c].rgbtGreen;
                        sum_pix_rgbtRed += image[r][c].rgbtRed;
                        divisor++;
                    }
                }
            }

            if (divisor != 0)
            {   
                // write data to buffer
                buffer[row % 3][col].rgbtBlue = (int)roundf(sum_pix_rgbtBlue / (float)divisor);
                buffer[row % 3][col].rgbtGreen = (int)roundl(sum_pix_rgbtGreen / (float)divisor);
                buffer[row % 3][col].rgbtRed = (int)roundf(sum_pix_rgbtRed / (float)divisor);
                // test
                //printf("write_to_buffer: position row=%i, col=%i, values BGR = %i, %i, %i\n", row % 3, col, buffer[row % 3][col].rgbtBlue, buffer[row % 3][col].rgbtGreen, buffer[row % 3][col].rgbtRed);
            }
            else
            {
                fprintf(stderr, "division by zero error\n");
                return;
            }

        }
    }
    // buffer postproduction (now we red all heigh lines to buffer/image)
    // test
    // printf("buffer postproducion\n");
    int buffer_point = (height - 1) % 3;
    for (int line = height - buffer_size; line < height; line++)
    {
        for (int column = 0; column < width; column++)
        {   
            image[line][column] = buffer[(buffer_point + 1) % 3][column];
            
            // test
            // printf("write to image position %i, %i, form bufer position %i, %i\n", line, column, (buffer_point + 1) % 3, column);
        }
        buffer_point++;
    }
    free(buffer);
    return;
}

// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{   

    // Sobel coeficients
    int box_gx[] = {-1, 0, 1, -2, 0, 2, -1, 0, 1};
    int box_gy[] = {-1, -2, -1, 0, 0, 0, 1, 2, 1};

    // Allocate memory for buffer image - line size = (3 px * width) - to make shure that processed pixels have no effect to neighbors
    int buffer_size = 3;
    
    RGBTRIPLE(*buffer)[width] = calloc(buffer_size, width * sizeof(RGBTRIPLE));
    if (buffer == NULL)
    {
        fprintf(stderr, "Not enough memory to store image.\n");
        return;
    }

    // number of written lines - buffer count is row here

    // walk trough pixels in the image
    for (int row = 0; row < height; row++)
    {
        // write buffer line to image if row > 3 (3 - buffer_size)
        if (row - buffer_size >= 0)
        {   
            for (int column = 0; column < width; column++)
            {   
                image[row - buffer_size][column] = buffer[row % 3][column];
            }
            // test
            // printf("write line from buffer on image=%i, buffer_ptr=%i\n", row - buffer_size, row % 3);
        } 

        for (int col = 0; col < width; col++)
        {
            //test
            //printf("process pixel row=%i, col=%i\n\n", row, col);
            // for each pixel
            int box_index = 0;
            int gx_b = 0;
            int gy_b = 0;
            int gx_g = 0;
            int gy_g = 0;
            int gx_r = 0;
            int gy_r = 0;

            // create 3x3 box
            for (int r = row - 1; r <= row + 1; r++)
            {
                for (int c = col - 1; c <= col + 1; c++)
                {   
                    // test
                    //printf("box r=%i, c=%i\n", r, c);
                    // if pixel is out of image - think it is black and have no effect to gx gy - go further
                    if (r < 0 || c < 0 || r > height - 1 || c > width - 1)
                    {
                       
                        box_index++;
                        // test
                        //printf("pixel out of range - continue, box index increase and %i\n", box_index);
                        continue;
                    }
                    else
                    {   
                        gx_b += box_gx[box_index] * image[r][c].rgbtBlue;
                        gx_g += box_gx[box_index] * image[r][c].rgbtGreen;
                        gx_r += box_gx[box_index] * image[r][c].rgbtRed;
                        
                        gy_b += box_gy[box_index] * image[r][c].rgbtBlue;
                        gy_g += box_gy[box_index] * image[r][c].rgbtGreen;
                        gy_r += box_gy[box_index] * image[r][c].rgbtRed;

                        box_index++;
                        // test
                        //printf("gx_b=%i, gx_g=%i, gx_r=%i, gy_b=%i, gy_g=%i, gy_r=%i, increased box index=%i\n", gx_b, gx_g, gx_r, gy_b, gy_g, gy_r, box_index);

                    }
                }
            }
            
           
            // write data to buffer
            buffer[row % 3][col].rgbtBlue = min((int)round(sqrt(pow(gx_b, 2) + pow(gy_b, 2))), 255);
            buffer[row % 3][col].rgbtGreen = min((int)round(sqrt(pow(gx_g, 2) + pow(gy_g, 2))), 255);
            buffer[row % 3][col].rgbtRed = min((int)round(sqrt(pow(gx_r, 2) + pow(gy_r, 2))), 255);
            // test
            //printf("treat pixel. final blue=%i, green=%i, red=%i\n", image[row][col].rgbtBlue, image[row][col].rgbtGreen, image[row][col].rgbtRed);
        }
    }
    // buffer postproduction (now we red all heigh lines to buffer/image)
    // test
    // printf("buffer postproducion\n");
    int buffer_point = (height - 1) % 3;
    for (int line = height - buffer_size; line < height; line++)
    {
        for (int column = 0; column < width; column++)
        {   
            image[line][column] = buffer[(buffer_point + 1) % 3][column];
            
            // test
            // printf("write to image position %i, %i, form bufer position %i, %i\n", line, column, (buffer_point + 1) % 3, column);
        }
        buffer_point++;
    }
    free(buffer);
    return;
}
