import os
import logging
import json
from typing import List, Dict, Any
from app.services.s3_service import S3Service
from app.services.ocr_service import OCRService
from app.services.llm import LLMService
from app.config import storage_config, llm_config
from app.models import MCQOption, MCQQuestion, MCQList
from app.tools.video_creation_tool import create_video

logger = logging.getLogger(__name__)

class MCQService:
    """
    Service to handle multiple-choice question generation from documents
    """

    @staticmethod
    def process_mcq_request(project_id: str, system_prompt: str, 
                          asset_files: List[str], user_prompt: str) -> Dict[str, Any]:
        """
        Process an MCQ generation request
        
        Args:
            project_id (str): The project ID
            system_prompt (str): System prompt for the LLM
            asset_files (List[str]): List of S3 file URLs
            user_prompt (str): User prompt for the LLM
            
        Returns:
            Dict[str, Any]: Generated MCQ content
        """
        try:
            # Create project directory
            project_dir = os.path.join(storage_config.mcq_files_path, project_id)
            os.makedirs(project_dir, exist_ok=True)
            
            # Download and process each asset file
            processed_texts = []
            downloaded_files = []
            
            logger.info(f"Processing {len(asset_files)} asset files for project {project_id}")
            
            for file_url in asset_files:
                try:
                    # Download the file
                    local_path = S3Service.download_from_public_url(file_url, project_dir)
                    downloaded_files.append(local_path)
                    
                    # Extract text using OCR
                    text_content = OCRService.extract_text(local_path)
                    processed_texts.append(text_content)
                    
                    logger.info(f"Successfully processed file: {file_url}")
                except Exception as e:
                    logger.error(f"Error processing file {file_url}: {str(e)}")
            
            # Combine all extracted texts
            combined_text = "\n\n".join(processed_texts)
            
            # Generate MCQs using LLM
            mcqs: MCQList = MCQService._generate_mcqs(system_prompt, combined_text, user_prompt)
            
            # Debug: Check the type and structure of mcqs
            logger.info(f"Type of mcqs: {type(mcqs)}")
            logger.info(f"Type name: {type(mcqs).__name__}")
            logger.info(f"mcqs content preview: {str(mcqs)[:200]}...")
                
            logger.info(f"MCQ generation complete for project {project_id}")
            # Call the video creation tool to create a video from the MCQs

            mcq_list = mcqs.raw # Extract the raw MCQ list from the MCQList object
            video_result = create_video(
                title=f"MCQ Video - {project_id}",
                desc="Automatically generated multiple choice questions video",
                thumbnail_text="MCQ Quiz",
                thumbnail_visual_desc="Educational quiz thumbnail with question marks and colorful design",
                video_type="mcq",
                raw=mcq_list,  # Pass the MCQList object
                project_id=project_id
            )

            logger.info(f"Video creation result: {video_result}")
            # Return the results
            return {
                "project_id": project_id,
                "mcqs": mcqs,
                "processed_files": len(downloaded_files),
            }
            
        except Exception as e:
            logger.error(f"Error processing MCQ request: {str(e)}")
            raise
    
    @staticmethod
    def _generate_mcqs(system_prompt: str, document_text: str, user_prompt: str) -> dict:
        """
        Generate MCQs using the LLM with structured output
        
        Args:
            system_prompt (str): System prompt for the LLM
            document_text (str): Extracted text from documents
            user_prompt (str): User prompt for the LLM
            
        Returns:
            dict: Generated MCQs
        """
        try:
            # Truncate document text if it's too long (context window limits)
            max_chars = 20000  # Approximate limit - adjust based on your model
            if len(document_text) > max_chars:
                document_text = document_text[:max_chars] + "...[truncated]"
            
            # Prepare content for the LLM
            full_prompt = f"""
            {system_prompt}
            
            DOCUMENT CONTENT:
            {document_text}
            
            USER QUERY:
            {user_prompt}
            """
            
            # Call the LLM for MCQ generation
            llm = LLMService(llm_config.provider, llm_config.model_name, llm_config.api_key)
            model = llm.model
            logger.info("Generating MCQs using LLM (structured output)...")
            logger.info(f"Full prompt length: {len(full_prompt)} characters")
            logger.debug(f"Full prompt content: {full_prompt[:500]}...")  # Log first 500 chars for debugging
            
            # Use structured output
            structured_llm = model.with_structured_output(MCQList)
            response = structured_llm.invoke(full_prompt)
            
            # Debug: Check what we got from the LLM
            logger.info(f"LLM response type: {type(response)}")
            logger.info(f"LLM response type name: {type(response).__name__}")
            
            result = response
            
            return result
        except Exception as e:
            logger.error(f"Error generating MCQs: {str(e)}")
            raise
