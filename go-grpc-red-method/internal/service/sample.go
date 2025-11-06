package service

import (
	"context"
	"fmt"
	"math/rand"
	"sync"

	pb "github.com/nissy-dev/sandbox/go-grpc-red-method/proto/gen/go/proto"
)

type SampleService struct {
	mu    sync.Mutex
	users map[string]*pb.User

	pb.UnimplementedSampleServiceServer
}

func NewSampleService() *SampleService {
	return &SampleService{
		users: make(map[string]*pb.User),
	}
}

func (s *SampleService) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	user, ok := s.users[req.Id]
	if !ok {
		return nil, fmt.Errorf("user not found")
	}
	return &pb.GetUserResponse{User: user}, nil
}

func (s *SampleService) CreateUser(ctx context.Context, req *pb.CreateUserRequest) (*pb.CreateUserResponse, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	user := &pb.User{
		Id:   fmt.Sprintf("%d", rand.Intn(1000)),
		Name: req.Name,
	}
	s.users[user.Id] = user
	return &pb.CreateUserResponse{User: user}, nil
}
