from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
from app.core.security import get_current_user
from app.models.user import User
from app.services.collaboration import CollaborationService
from app.core.logging import logger
import json

router = APIRouter()
collaboration_service = CollaborationService()

@router.websocket("/documents/{document_id}/collaborate")
async def collaborate(
    websocket: WebSocket,
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """WebSocket endpoint for real-time collaboration"""
    try:
        # Accept connection
        await websocket.accept()
        
        # Join collaboration session
        await collaboration_service.join_session(
            document_id=document_id,
            user_id=current_user.id,
            websocket=websocket
        )
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message["type"] == "typing_start":
                    await collaboration_service.start_typing(
                        document_id=document_id,
                        user_id=current_user.id
                    )
                elif message["type"] == "typing_stop":
                    await collaboration_service.stop_typing(
                        document_id=document_id,
                        user_id=current_user.id
                    )
                elif message["type"] == "cursor_update":
                    await collaboration_service.update_cursor(
                        document_id=document_id,
                        user_id=current_user.id,
                        position=message["position"]
                    )
                elif message["type"] == "content_update":
                    await collaboration_service.update_content(
                        document_id=document_id,
                        user_id=current_user.id,
                        content=message["content"]
                    )
                elif message["type"] == "selection_update":
                    await collaboration_service.update_selection(
                        document_id=document_id,
                        user_id=current_user.id,
                        selection=message["selection"]
                    )
                
        except WebSocketDisconnect:
            # Handle disconnection
            await collaboration_service.leave_session(
                document_id=document_id,
                user_id=current_user.id
            )
            
    except Exception as e:
        logger.error(f"Error in collaboration websocket: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to establish collaboration session"
        )

@router.get("/documents/{document_id}/collaborators", response_model=List[Dict[str, Any]])
async def get_collaborators(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get active collaborators for a document"""
    try:
        collaborators = await collaboration_service.get_collaborators(
            document_id=document_id,
            user_id=current_user.id
        )
        return collaborators
    except Exception as e:
        logger.error(f"Error getting collaborators: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get collaborators"
        )

@router.get("/documents/{document_id}/typing", response_model=List[str])
async def get_typing_users(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get users currently typing in the document"""
    try:
        typing_users = await collaboration_service.get_typing_users(
            document_id=document_id,
            user_id=current_user.id
        )
        return typing_users
    except Exception as e:
        logger.error(f"Error getting typing users: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get typing users"
        )

@router.get("/documents/{document_id}/cursors", response_model=Dict[str, Dict[str, Any]])
async def get_cursors(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get cursor positions for all collaborators"""
    try:
        cursors = await collaboration_service.get_cursors(
            document_id=document_id,
            user_id=current_user.id
        )
        return cursors
    except Exception as e:
        logger.error(f"Error getting cursors: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get cursors"
        )

@router.get("/documents/{document_id}/selections", response_model=Dict[str, Dict[str, Any]])
async def get_selections(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get text selections for all collaborators"""
    try:
        selections = await collaboration_service.get_selections(
            document_id=document_id,
            user_id=current_user.id
        )
        return selections
    except Exception as e:
        logger.error(f"Error getting selections: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get selections"
        )

@router.post("/documents/{document_id}/lock")
async def lock_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Lock document for editing"""
    try:
        await collaboration_service.lock_document(
            document_id=document_id,
            user_id=current_user.id
        )
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error locking document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to lock document"
        )

@router.post("/documents/{document_id}/unlock")
async def unlock_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Unlock document"""
    try:
        await collaboration_service.unlock_document(
            document_id=document_id,
            user_id=current_user.id
        )
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error unlocking document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to unlock document"
        ) 