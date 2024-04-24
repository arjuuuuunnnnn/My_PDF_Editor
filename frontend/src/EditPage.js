import React from "react";

import "./editpage.css";
import renderHTML from "react-render-html";
// import { history } from "./history";
import { EmptyPage } from "./empty404";
// import Draggable from "react-draggable"; // The default


// Redux
import { bindActionCreators } from "redux";
import { connect } from "react-redux";

class HomePage extends React.Component {
  constructor(props) {
    super(props);
  }

  printPage() {
    var mywindow = window.open("", "PRINT", "height=400,width=600");

    mywindow.document.write(
      document.getElementById("print-edit-container").innerHTML
    );

    mywindow.document.close(); // necessary for IE >= 10
    mywindow.focus(); // necessary for IE >= 10*/

    mywindow.print();
    mywindow.close();

    return true;
  }

  errorpage() {
    return (
      <div>
        <EmptyPage />
      </div>
    );
  }

  renderPdfEditor() {
    return (
      <div className="page-container">
        <div className="top-nav"></div>
        <div id="print-edit-container" className="edit-container">
          {renderHTML(this.props.data.data)}
        </div>
      </div>
    );
  }

  render() {
    console.log("Data in render():", this.props.data.data);
  
    return (
      <div className="edit-page-container">
        <div className="navbar">
          <nav className="main-menu">
            <ul>
              <li className="has-subnav" onClick={() => this.printPage()}>
                <a href="#">
                  <i className="fa fa-laptop fa-2x">
                    <img
                      src="https://cdn1.iconfinder.com/data/icons/arrows-vol-1-4/24/download_1-512.png"
                      width={25}
                      height={25}
                    />
                  </i>
                  <span className="nav-text">Save & Download</span>
                </a>
              </li>
            </ul>
          </nav>
        </div>
  
        <div contentEditable="true">
          {this.props.data.data ? this.renderPdfEditor() : this.errorpage()}
        </div>
      </div>
    );
  }
  
  
}

const mapStateToProps = (state) => {
  const { data } = state;
  state.data = data;
  console.log("Data in mapStateToProps:", data.data);
  return { data };
};


const mapDispatchToProps = (dispatch) =>
  bindActionCreators(
    {
      // Actions go here
    },
    dispatch
  );

export default connect(mapStateToProps, mapDispatchToProps)(HomePage);
