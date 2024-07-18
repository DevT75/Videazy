import axios from "axios"

const URL = import.meta.env.API_URL || "https://videazy.onrender.com";

export const uploadFiles = async (files,setCompressed) => {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
    }
    // console.log(formData);
    try {
        const response = await axios.post(`${URL}/upload/`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        console.log(response.data);
        for (let i = 0; i < response.data.length; i++) setCompressed(map => new Map(map.set(response.data[i].filename, response.data[i].url)));
    } catch (error) {
        console.error("Error uploading files:", error);
    }
};

// export const