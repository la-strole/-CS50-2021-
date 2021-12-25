#include <stdio.h>
#include <stdli
#include <inttypes.h>

uint32_t jenkins_one_at_a_time_hash(const uint8_t* key, size_t length);

int main(void)
{
    for (int i = 0; i < 26; i++)
    {   
        unsigned char c = i + 97;
        uint32_t hash = jenkins_one_at_a_time_hash(&c, 1);
        char buffer[sizeof(sizeof(unsigned int)*8+1)];
        char * str = 
        
    }
}

uint32_t jenkins_one_at_a_time_hash(const uint8_t* key, size_t length) 
{

    size_t i = 0;
    uint32_t hash = 0;
    while (i != length) 
    {
        hash += key[i++];
        hash += hash << 10;
        hash ^= hash >> 6;
    }
    hash += hash << 3;
    hash ^= hash >> 11;
    hash += hash << 15;
    
    return hash;
}
