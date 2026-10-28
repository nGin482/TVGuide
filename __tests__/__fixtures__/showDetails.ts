import ShowDetails from "../../database/models/ShowDetails";
import { ShowDetails as TShowDetails } from "../../types";


export const testShowDetailsData: TShowDetails[] = [
  {
    id: 1,
    description: "",
    genres: [],
    image: "",
    title: "Merlin",
    tvmazeId: "1",
  },
  {
    id: 2,
    description: "",
    genres: [],
    image: "",
    title: "Endeavour",
    tvmazeId: "2",
  },
];


export const testShowDetails = (showDetails = testShowDetailsData) => {
  return showDetails.map(showDetail => ShowDetails.build({
    title: showDetail.title,
    description: showDetail.description,
    genres: showDetail.genres,
    image: showDetail.image,
    tvmazeId: showDetail.tvmazeId,
  }));
};
