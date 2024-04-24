const initialState = {
  data: null // Initialize data as null or as per your requirements
};

export default (state = initialState, action) => {
  switch (action.type) {
    case "HTML_DATA":
      return {
        ...state,
        data: action.payload,
      };
    default:
      return state;
  }
};
