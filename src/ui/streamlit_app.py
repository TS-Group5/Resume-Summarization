import os
from tempfile import NamedTemporaryFile

import requests
import streamlit as st
import yaml

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Configure page
st.set_page_config(
    page_title="Resume Video Script Generator", page_icon="🎥", layout="wide"
)


def main():
    st.title("Resume Video Script Generator 🎥")

    # Template selection
    template_type = st.selectbox(
        "Select Resume Template Type", ["ATS/HR Resume", "Industry Manager Resume"]
    )

    st.sidebar.header("About")
    st.sidebar.info(
        "This application generates video scripts from resume templates. "
        "Select your template type and upload your resume to get started."
    )

    # Main content
    st.header("Generate Video Script")

    # Convert selection to API parameter
    template_param = "ats" if template_type == "ATS/HR Resume" else "industry"

    # File uploader
    uploaded_file = st.file_uploader(
        f"Upload your {template_type}",
        type=config["file"]["allowed_extensions"],
        help=f"Upload your resume in {', '.join(config['file']['allowed_extensions'])} format",
    )

    if uploaded_file:
        st.success("File uploaded successfully!")

        # Display file info
        st.write("File details:")
        st.json(
            {
                "Filename": uploaded_file.name,
                "Size": f"{uploaded_file.size / 1024:.2f} KB",
                "Type": uploaded_file.type,
                "Template": template_type,
            }
        )

        # Generate button
        if st.button("Generate Video Script", type="primary"):
            with st.spinner("Generating video script..."):
                try:
                    # Create API request with template type
                    files = {"file": uploaded_file}
                    data = {"template_type": template_param}

                    # Save the uploaded file temporarily
                    temp_file = NamedTemporaryFile(delete=False, suffix=".docx")
                    temp_file.write(uploaded_file.getvalue())
                    temp_file.close()

                    # Make API request
                    with open(temp_file.name, "rb") as f:
                        api_url = f"{config['api']['base_url']}{config['api']['endpoints']['generate_script']}"
                        response = requests.post(api_url, files={"file": f}, data=data)

                    # Clean up temp file
                    os.unlink(temp_file.name)

                    if response.status_code == 200:
                        data = response.json()

                        # Display results
                        st.header("Generated Script")
                        st.info(f"Template Type: {data['template_type']}")

                        # Display script in a text area
                        st.text_area(
                            "Generated Script",
                            value=data["script"],
                            height=300,
                            disabled=True,
                        )

                        # Add download button
                        st.download_button(
                            label="Download Script",
                            data=data["script"],
                            file_name=f"{template_type.lower().replace('/', '_')}_script.txt",
                            mime="text/plain",
                        )

                        # Add helpful tips based on template type
                        if template_type == "ATS/HR Resume":
                            st.info(
                                "💡 Tip: This script is optimized for HR and recruitment "
                                "audiences, focusing on skills and achievements."
                            )
                        else:
                            st.info(
                                "💡 Tip: This script is tailored for industry management "
                                "roles, emphasizing leadership experience and strategic "
                                "accomplishments."
                            )
                    else:
                        st.error(f"Error: {response.json()['detail']}")

                except Exception as e:
                    st.error(f"Error connecting to the API: {str(e)}")


if __name__ == "__main__":
    main()
