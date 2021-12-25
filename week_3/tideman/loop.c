
#include <stdio.h>

const int candidate_count = 5;

// ajencety matrix
int locked[5][5];

int visited_nodes_index = 0;
// result for new base case - if result = 0 - return 0

int result = 1;

int loop_test(int node, int winner, int visited_nodes[candidate_count], int r);

int main() 
{
  // initialize array 

  
  for (int i = 0; i < candidate_count; i++)
  {
    for (int j = 0; j < candidate_count; j++)
    {
      locked[i][j] = 0;
    }
  }

  // initialize ajencety matrix

  locked[0][1] = 1;
  locked[1][2] = 1;
  locked[2][4] = 1;
  locked[2][3] = 1;
  
  // initialize visited nodes array
  int visited_nodes[5];
  for (int i = 0; i < candidate_count; i++)
  {
      visited_nodes[i] = -1;
  }
  
  // new edge
  int winner = 3;
  int loser = 0;
 
  int ret = loop_test(loser, winner, visited_nodes, result);
  printf("result is %i\n", ret);

  return 0;
}

int loop_test(int node, int winner, int visited_nodes[candidate_count], int r)
{

  // test
  printf("loop test: node = %i, result = %i, visited nodes = ", node, r);

  for (int i = 0; i < candidate_count; i++)
  {
    printf("%i, ", visited_nodes[i]);
  }
  printf("\n");


  int answer = 1;

  // base case 
  
  if (node == winner)
    {
      answer = 0;
      return result * answer;
    }

  else if (result == 0)
    {
      answer = 0;
      return result * answer;
    }

  // went trough child in ajencity matrix
  for (int i = 0; i < candidate_count; i++)
  {
    if (locked[node][i] == 1)
    {
      int visited = 0;
      for (int j = 0; j < candidate_count; j++)
      {
        if (visited_nodes[j] == node)
          {
            visited = 1;
          }
      }
      if (visited != 1)
        {
          visited_nodes[visited_nodes_index] = node;
          visited_nodes_index += 1;
          return loop_test(i, winner, visited_nodes, result);
        }
    }
  }
  answer = 1;
  return result * answer;
}