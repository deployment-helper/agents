import os
import logging
import json
from typing import List, Dict, Any
from app.services.s3_service import S3Service
from app.services.ocr_service import OCRService
from app.services.llm import LLMService
from app.config import storage_config, llm_config

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
            mcqs = MCQService._generate_mcqs(system_prompt, combined_text, user_prompt)
            
            # Save results
            result_path = os.path.join(project_dir, "mcq_results.json")
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(mcqs, f, indent=2)
            
            logger.info(f"MCQ generation complete for project {project_id}")
            
            # Return the results
            return {
                "project_id": project_id,
                "mcqs": mcqs,
                "processed_files": len(downloaded_files),
                "result_file_path": result_path
            }
            
        except Exception as e:
            logger.error(f"Error processing MCQ request: {str(e)}")
            raise
    
    @staticmethod
    def _generate_mcqs(system_prompt: str, document_text: str, user_prompt: str) -> Dict[str, Any]:
        """
        Generate MCQs using the LLM
        
        Args:
            system_prompt (str): System prompt for the LLM
            document_text (str): Extracted text from documents
            user_prompt (str): User prompt for the LLM
            
        Returns:
            Dict[str, Any]: Generated MCQs
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
            response = model.predict(full_prompt)
            
            # Try to parse the response as JSON
            try:
                # Check if the response is JSON or convert it
                if response.strip().startswith('{') and response.strip().endswith('}'):
                    return json.loads(response)
                else:
                    # Return as raw text if not JSON
                    return {"raw_response": response}
            except json.JSONDecodeError:
                # If not valid JSON, return as raw text
                return {"raw_response": response}
            
        except Exception as e:
            logger.error(f"Error generating MCQs: {str(e)}")
            raise
