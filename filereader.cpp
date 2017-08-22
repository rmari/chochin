#include <vector>
#include <unordered_map>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

struct Frame {
  std::unordered_map <std::string, std::vector < float > >  positions;
  std::unordered_map <std::string, std::vector < float > > thicknesses;
  std::unordered_map <std::string, std::vector < std::vector < float > > > colors;
  std::unordered_map <std::string, std::vector < int > > layers;
  std::unordered_map <std::string, std::vector < std::string > > texts;
};


class filereader {
private:
  std::ifstream in_file;
  int layer;
  std::vector < float > color; // rgba
  float thickness;
  // std::vector <struct Color> palette;
  std::vector < std::vector < float > > palette;

public:
  // std::map <std::string, std::vector < std::vector < float > > > positions;
  std::vector < struct Frame > frames;
  filereader(std::string fname) :
  layer(1),
  color({0,0,0,0}),
  thickness(1)
  {
    in_file.open(fname.c_str(), std::ifstream::in);
    if (!in_file.is_open()) {
      throw std::runtime_error("Could not open file.\n ");
    }
  };
  ~filereader(){
    in_file.close();
  };

  void setPalette(const std::vector < std::vector < float > > &color_palette){
    palette = color_palette;
    // for (auto p: palette){
    //   std::cout << p[0] << " " <<  p[1] << " " << p[2] << " " << p[3]  << std::endl;
    // }
  }

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

  void getColor(std::istringstream &sline) {
    std::string line;
    std::getline(sline, line);
    std::istringstream remaining(line);
    float component;
    std::vector<float> col;
    while(remaining >> component) {
      col.push_back(component);
    }

    if (col.size() == 1) {           // by label
      color = palette[col[0]];
    } else if (col.size() == 3) {    // by rgb
      col.push_back(1);
      color = col;
    } else if (col.size() == 4) {    // by rgba
      color = col;
    }
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
        getColor(sline);
      } else if (cmd == "r") {
        sline >> thickness;
      } else {
        std::cout << "[chochin] unrecognized command \"" << line <<  "\"" << std::endl;
      }
    }
    return !empty;
  };

};
