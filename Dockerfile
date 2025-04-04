FROM python:3.9
 
 # Set the working directory in the container
 WORKDIR /app
 RUN apt-get update && apt-get install -y python3-opencv
 RUN pip install opencv-python
 # Copy the current directory contents into the container at /app
 COPY requirements.txt ./
 RUN pip install -r requirements.txt
 
 # Copy everything else
 COPY . .
 
 # Expose the port that Streamlit uses
 EXPOSE 8080
 
 # Start the Streamlit app
 CMD streamlit run web.py --server.port=8080 --server.address=0.0.0.0 --server.headless=true
