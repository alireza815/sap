#ifndef CCONSTRAINEDNJLIB_H
#define CCONSTRAINEDNJLIB_H

class TooFewAlnBasesError: public std::exception
{
  virtual const char* what() const throw()
  {
    return "TooFewAlnBasesError";
  }
} TooFewAlnBasesError; // This name can also be a short name for the class. It has to bere there for some reason so we just make it hte same as the class name.

class Node {
public:
  Node();
/*   ~Node();
 */
  Node *left;
  Node *right;     /* right children, or None */
  void assignLeft (Node);
  void assignRight (Node);
  Node getRight (void);
  Node getLeft (void);
  int name;
  double distLeft;  /* Length of edges to the children, if any */
  double distRight;
  std::set<int> leafSet;     /* list of subnodes as set in each node */
  char *getSubTreeString(char *);
};  

class K2Pstats {
public:
  int transitions;
  int transversions;
  int alignedBases;
};

K2Pstats k2pStats(int, int, int, char **, int *);
double k2pDist(K2Pstats, int, char **, int *);
double computeDistance(int, int, int, char **, int *);
double resampleDistance(int, int, int, char **, int *);
double calcRsum(int, double **);
void computeAllowedPairs(void);
void updateAllowedPairs(int, int);
bool updateConstraints(int, int);
void updateMatrices(int, int);
int *findPair(double **, std::list<int *>);
void createParentNode(int, int);
char *compute(int, char **, int, char **, int);
void initCache(int);

int main(void);

#endif
