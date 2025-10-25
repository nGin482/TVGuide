import { useContext, useEffect, useState } from "react";
import { useParams } from "react-router";
import { Helmet } from "react-helmet";
import { Alert, App, Button, List, Modal, Space, Spin, Typography } from "antd";

import TVGuide from "../components/TVGuide";
import { SubscriptionForm } from "../components/SubscriptionForm";
import { SearchItemTag } from "../components/SearchItemTag";
import { SearchItem } from "../components/SearchItem";
import { UserContext } from "../contexts/UserContext";
import {
    addSubscriptions,
    getGuide,
    getUser,
    getUserSubscriptions,
    unsubscribeFromSearch
} from "../requests";
import { handleErrorResponse } from "../utils";
import {
    Guide,
    SubscriptionsPayload,
    SubscriptionsAction,
    User,
    UserSearchSubscription,
    SearchItem as TSearchItem
} from "../utils/types";
import "../styles/ProfilePage.css";

interface UserParam {
    user: string
}

const ProfilePage = () => {
    const { user } = useParams<UserParam>();
    const { currentUser, setUser } = useContext(UserContext);
    
    const [viewingOwnProfile, setViewingOwnProfile] = useState(false);
    const [userDetails, setUserDetails] = useState<User>(null);
    const [loadingUser, setLoadingUser] = useState(false);
    const [userTVGuide, setUserTVGuide] = useState<Guide>(null);
    const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);
    const [viewSubscription, setViewSubscription] = useState<TSearchItem>(null);
    
    const { notification } = App.useApp();
    const { Text } = Typography;
    
    useEffect(() => {
        if (user) {
            setLoadingUser(true);
            fetchUser(user);
            fetchUserSubscriptions(user);
            fetchGuide();
        }
    }, [user]);

    useEffect(() => {
        if (user && currentUser && user === currentUser.username) {
            setViewingOwnProfile(true);
        }
    }, [user, currentUser]);

    const fetchUser = async (username: string) => {
        const user = await getUser(username);
        setUserDetails(user);
        setLoadingUser(false);
    };

    const fetchUserSubscriptions = async (username: string) => {
        await getUserSubscriptions(username);
    };

    const fetchGuide = async () => {
        const guide = await getGuide();
        setUserTVGuide(guide);
    };

    const toggleModal = () => {
        setShowSubscriptionModal(current => !current);
    };

    const unsubscribe = async (subscriptionId: number) => {
        const payload: SubscriptionsPayload = {
            unsubscribe: {
                subscriptionId
            }
        };
        updateSubscriptionsHandle(payload, "unsubscribe");
    };

    const updateSubscriptionsHandle = async (
        subscriptionsPayload: SubscriptionsPayload,
        action: SubscriptionsAction
    ) => {
        try {
            let updatedUserDetails: User;
            if (action === "unsubscribe") {
                const subscriptionId = subscriptionsPayload.unsubscribe.subscriptionId;
                await unsubscribeFromSearch(currentUser.username, subscriptionId);
                updatedUserDetails = {
                    ...userDetails,
                    show_subscriptions: userDetails.show_subscriptions.filter(
                        subscription => subscription.id !== subscriptionId
                    )
                };
            }
            else {
                const subscriptions = subscriptionsPayload.subscribe.show_subscriptions;
                updatedUserDetails = await addSubscriptions(currentUser.username, subscriptions);
            }
            setUserDetails(updatedUserDetails);
            notification.success({
                message: "Success!",
                description: "Your subscriptions have been updated",
            });
        }
        catch(error) {
            console.error(error)
            let errorMessage: string = error?.message;
            if (error?.response) {
                errorMessage = handleErrorResponse(error, "update your subscriptions");
            }
            notification.error({
                message: "An error occurred updating your show subscriptions!",
                description: <Text>{errorMessage}</Text>
            });
        }
    };

    const subscriptionActions = (subscription: UserSearchSubscription) => {
        const actions = [
            <Button onClick={() => setViewSubscription(subscription.search_item)}>View</Button>
        ];

        if (viewingOwnProfile) {
            actions.push(<Button onClick={() => unsubscribe(subscription.id)}>Unsubscribe</Button>);
        }

        return actions;
    };

    return (
        userDetails ? (
            <>
                <Helmet>
                    <title>{userDetails.username} Profile | TVGuide</title>
                </Helmet>
                <h1>{userDetails.username}</h1>
                {viewingOwnProfile && userTVGuide && (
                    <TVGuide
                        user={userDetails}
                    />
                )}
                <div id="subscription-list-container">
                    <List
                        bordered
                        dataSource={userDetails.show_subscriptions}
                        renderItem={item => (
                            <List.Item
                                actions={subscriptionActions(item)}
                            >
                                <div className="search-item-subscription">
                                    <Text>{item.search_item.show}</Text> {" "}
                                    <SearchItemTag searchItem={item.search_item} />
                                </div>
                            </List.Item>
                        )}
                        header={<strong>{viewingOwnProfile ? 'Your' : `${user}'s`} Show Subscriptions</strong>}
                        className="subscription-list"
                        footer={viewingOwnProfile && (
                            <Space>
                                <Button onClick={() => toggleModal()}>Subscribe to a Show</Button>
                            </Space>
                        )}
                        itemLayout="vertical"
                    />
                </div>
                <SubscriptionForm
                    showForm={showSubscriptionModal}
                    userDetails={userDetails}
                    toggleModal={toggleModal}
                    updateSubscriptionsHandle={updateSubscriptionsHandle}
                />
                <Modal
                    open={viewSubscription != null}
                    cancelButtonProps={{ style: { display: "none" } }}
                    onOk={() => setViewSubscription(null)}
                    width="fit-content"
                    closeIcon={null}
                >
                    <SearchItem 
                        searchItem={viewSubscription}
                        show={viewSubscription?.show || ""}
                        setShowData={null}
                    />
                </Modal>
            </>
        )
        : !loadingUser && !userDetails ? (
            <Alert
                type="error"
                className="user-alert"
                message="Error!"
                description={`An account with the username ${user} could not be found`}
            />
        ) : (
            <Spin fullscreen />
        )
    );
};

export default ProfilePage;