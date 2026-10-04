import { Modal } from "antd";


interface ConfirmationModalProps {
  confirmText: string;
  isOpen: boolean;
  message: string;
  title: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmationModal = (props: ConfirmationModalProps) => {


  return (
    <Modal
      title={props.title}
      open={props.isOpen}
      onOk={props.onConfirm}
      onCancel={props.onCancel}
      okText={props.confirmText}
      cancelText={props?.cancelText ?? "Cancel"}
    >
      {props.message}
    </Modal>
  );
};

export default ConfirmationModal;