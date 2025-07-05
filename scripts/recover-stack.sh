#!/bin/bash
# Script to recover a CloudFormation stack in UPDATE_FAILED state

# Set variables
STACK_NAME="pc-builder"

echo "🔍 Checking current stack status..."
STACK_STATUS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].StackStatus" --output text 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "❌ Stack not found or AWS CLI not configured correctly."
    echo "Please check your AWS credentials and region settings."
    exit 1
fi

echo "📊 Current stack status: $STACK_STATUS"

# Function to show menu options
show_menu() {
    echo ""
    echo "📋 Recovery options:"
    echo "1) Continue update with rollback disabled (try to fix)"
    echo "2) Roll back to last known good state"
    echo "3) Delete stack and start fresh"
    echo "4) Exit"
    echo ""
    read -p "Select an option (1-4): " choice
}

# Main menu loop
show_menu
while true; do
    case $choice in
        1)
            echo "🔄 Continuing update with rollback disabled..."
            aws cloudformation continue-update-rollback --stack-name $STACK_NAME
            
            echo "⏱️ Waiting for stack to stabilize..."
            aws cloudformation wait stack-update-complete --stack-name $STACK_NAME
            
            echo "🔄 Attempting update with rollback disabled..."
            aws cloudformation update-stack \
                --stack-name $STACK_NAME \
                --use-previous-template \
                --parameters ParameterKey=Stage,UsePreviousValue=true \
                --disable-rollback
            
            echo "⏱️ Waiting for update to complete (this may take a while)..."
            aws cloudformation wait stack-update-complete --stack-name $STACK_NAME
            
            NEW_STATUS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].StackStatus" --output text)
            echo "📊 New stack status: $NEW_STATUS"
            
            if [[ "$NEW_STATUS" == "UPDATE_COMPLETE" ]]; then
                echo "✅ Stack recovery successful!"
            else
                echo "⚠️ Stack is now in $NEW_STATUS state. May need further actions."
            fi
            break
            ;;
        2)
            echo "⏪ Rolling back to last known good state..."
            aws cloudformation rollback-stack --stack-name $STACK_NAME
            
            echo "⏱️ Waiting for rollback to complete (this may take a while)..."
            aws cloudformation wait stack-rollback-complete --stack-name $STACK_NAME
            
            ROLLBACK_STATUS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].StackStatus" --output text)
            echo "📊 After rollback, stack status: $ROLLBACK_STATUS"
            break
            ;;
        3)
            read -p "⚠️ Are you sure you want to delete the stack? This cannot be undone. (y/n): " confirm
            if [[ $confirm == "y" || $confirm == "Y" ]]; then
                echo "🗑️ Deleting stack..."
                aws cloudformation delete-stack --stack-name $STACK_NAME
                
                echo "⏱️ Waiting for stack deletion to complete..."
                aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME
                
                if [ $? -eq 0 ]; then
                    echo "✅ Stack deleted successfully. You can now create a new stack from scratch."
                else
                    echo "❌ Stack deletion may have failed. Please check the AWS Console."
                fi
            else
                echo "❌ Stack deletion cancelled."
                show_menu
            fi
            break
            ;;
        4)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please select 1-4."
            show_menu
            ;;
    esac
done
