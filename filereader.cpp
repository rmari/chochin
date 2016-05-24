#include <vector>
#include <map>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

struct Frame {
  std::map <std::string, std::vector < float > >  positions;
  std::map <std::string, std::vector < float > > thicknesses;
  std::map <std::string, std::vector < int > > colors;
  std::map <std::string, std::vector < int > > layers;
  std::map <std::string, std::vector < std::string > > texts;
};

class filereader {
private:
  std::ifstream in_file;
  int layer;
  int color;
  float thickness;

public:
  // std::map <std::string, std::vector < std::vector < float > > > positions;
  std::vector < struct Frame > frames;
  filereader(std::string fname){
    in_file.open(fname.c_str(), std::ifstream::in);
  };
  ~filereader(){
    in_file.close();
  };

  // std::vector<float> fetch(std::istringstream &sline, unsigned int size){
  //   std::vector < float > read_vec (size);
  //   for(unsigned int i=0; i<size; i++){
  //     sline >> read_vec[i];
  //   }
  //   return read_vec;
  // };

  void getCircle(std::istringstream &sline, struct Frame &frame) {
    double coord;
    for (int i=0; i < 3; i++) {
      sline >> coord;
      frame.positions["c"].push_back(coord);
    }
    frame.thicknesses["c"].push_back(thickness);
    frame.colors["c"].push_back(color);
    frame.layers["c"].push_back(layer);
  };

  void getLine(std::istringstream &sline, struct Frame &frame) {
    double coord;
    for (int i=0; i < 6; i++) {
      sline >> coord;
      frame.positions["l"].push_back(coord);
    }
    frame.colors["l"].push_back(color);
    frame.layers["l"].push_back(layer);
  };

  void getString(std::istringstream &sline, struct Frame &frame) {
    double coord;
    for (int i=0; i < 6; i++) {
      sline >> coord;
      frame.positions["s"].push_back(coord);
    }
    frame.thicknesses["s"].push_back(thickness);
    frame.colors["s"].push_back(color);
    frame.layers["s"].push_back(layer);
  };

  void getText(std::istringstream &sline, struct Frame &frame) {
    double coord;
    for (int i=0; i < 3; i++) {
      sline >> coord;
      frame.positions["t"].push_back(coord);
    }
    frame.colors["t"].push_back(color);
    frame.layers["t"].push_back(layer);
    std::string t;
    std::getline(sline, t);
    frame.texts["t"].push_back(t);
  };

  bool get(){
    std::string cmd;
    struct Frame frame;
    frames.push_back(frame);

    bool empty = true;
    for (std::string line; std::getline(in_file, line); ) {
      if (line.empty()) {
        break;
      }
      empty = false;
      std::istringstream sline(line);
      sline >> cmd;
      struct Frame &new_frame = frames[frames.size()-1];
      if (cmd == "c") {
        getCircle(sline, new_frame);
      } else if (cmd == "s") {
        getString(sline, new_frame);
      } else if (cmd == "l") {
        getLine(sline, new_frame);
      } else if (cmd == "t") {
        getText(sline, new_frame);
      } else if (cmd == "y") {
        sline >> layer;
      } else if (cmd == "@") {
        sline >> color;
      } else if (cmd == "r") {
        sline >> thickness;
      } else {
        std::cout << "[ chochin ] unrecognized command " << line << std::endl;
      }
    }
    return !empty;
  };

};
